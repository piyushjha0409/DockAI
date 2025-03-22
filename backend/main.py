import io
import tempfile
import os
from fastapi.responses import JSONResponse
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from utils.llm_integration import generate_docking_report
from utils.pdf_generator import create_pdf_report
from typing import Optional, List, Dict
from ipfs.pinata_post import upload_to_pinata  # Import the Pinata upload function
from utils.parser import parse_autodock_results

load_dotenv()
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Application started successfully")


@app.post("/generate-report-pdf")
async def parse_docking_file(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        return JSONResponse(
            status_code=400, content={"error": "Only text files are supported"}
        )

    content = await file.read()
    content_str = content.decode("utf-8")

    try:
        parsed_data = parse_autodock_results(content_str)
        print(parsed_data)

        llm_report = generate_docking_report(parsed_data)
        print(llm_report)
        pdf_report = await create_pdf_report(llm_report)

        # Save the PDF to a temporary file
        # temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        # temp_file.write(pdf_report)
        # temp_file_path = temp_file.name
        # temp_file.close()

        # JWT Token for Pinata
        # PINATA_JWT_TOKEN = os.getenv("JWT")

        # Upload to Pinata and get the CID
        # cid = upload_to_pinata(temp_file_path, PINATA_JWT_TOKEN)
        # if not cid:
        #     raise HTTPException(status_code=500, detail="Failed to upload PDF to Pinata")

        # Clean up the temporary file
        # os.unlink(temp_file_path)

        # Return the CID along with the PDF file
        # return {
        #     "cid": cid,
        #     "pdf_report": Response(
        #         content=pdf_report,
        #         media_type="application/pdf",
        #         headers={
        #             "Content-Disposition": f"attachment; filename=docking_report_{file.filename}.pdf"
        #         }
        #     )
        # }
        return Response(
            content=pdf_report,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=docking_report_{file.filename}.pdf"
            },
        )
    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise
    except Exception as err:
        import traceback

        print(f"Error: {str(err)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=400, detail=f"Error processing PDB file: {str(err)}"
        )
