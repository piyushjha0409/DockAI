import io
import os
import tempfile
from typing import Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ipfs.pinata_post import upload_to_pinata  # Import the Pinata upload function
from utils.llm_integration import generate_docking_report
from utils.parser import parse_autodock_results
from utils.pdf_generator import create_pdf_report
# New imports for visualization
from utils.visualization import process_docking_visualization, create_visualization_data

load_dotenv()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        llm_report = generate_docking_report(parsed_data)
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


@app.post("/visualize-docking")
async def visualize_docking(
    result_file: UploadFile = File(...),
    pdbqt_file: UploadFile = File(...),
):
    """
    Process AutoDock Vina .txt and .pdbqt files to generate visualization data.
    
    Args:
        result_file: The AutoDock Vina output text file with binding affinities
        pdbqt_file: The PDBQT file containing 3D structural data
        
    Returns:
        JSON response with visualization data for frontend rendering
    """
    if result_file.content_type != "text/plain":
        return JSONResponse(
            status_code=400, content={"error": "Result file must be a text file"}
        )
        
    if not pdbqt_file.filename.endswith('.pdbqt'):
        return JSONResponse(
            status_code=400, content={"error": "Second file must be a PDBQT file"}
        )
    
    try:
        # Read the content of both files
        result_content = await result_file.read()
        result_content_str = result_content.decode("utf-8")
        
        pdbqt_content = await pdbqt_file.read()
        pdbqt_content_str = pdbqt_content.decode("utf-8")
        
        # Parse the AutoDock results
        parsed_data = parse_autodock_results(result_content_str)
        
        # Process the PDBQT file and create visualization data
        visualization_data = process_docking_visualization(parsed_data, pdbqt_content_str)
        
        # Create data structure for frontend visualization
        frontend_data = create_visualization_data(visualization_data)
        
        return JSONResponse(
            status_code=200,
            content=frontend_data
        )
        
    except Exception as err:
        import traceback
        print(f"Error: {str(err)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing docking visualization: {str(err)}"
        )
