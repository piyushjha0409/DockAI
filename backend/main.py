import io
import os
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ipfs.pinata_post import upload_to_pinata  # Import the Pinata upload function

# Import the Solana CID storage function
from utils.cid_store2 import store_cid_on_solana
from utils.llm_integration import generate_docking_report
from utils.parser import parse_autodock_results
from utils.pdf_generator import create_pdf_report

# New imports for visualization
from utils.visualization import create_visualization_data, process_docking_visualization

load_dotenv()
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dock-ai-frontend.vercel.app"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("Application started successfully")


@app.post("/process-docking-data")
async def process_docking_data(
    result_file: UploadFile = File(...),
    pdbqt_file: UploadFile = File(...),
):
    """
    Combined endpoint that processes AutoDock results to generate both PDF report
    and visualization data if PDBQT file is provided.

    Args:
        result_file: The AutoDock Vina output text file with binding affinities
        pdbqt_file: Optional PDBQT file containing 3D structural data for visualization

    Returns:
        JSON response with PDF report and visualization data (if PDBQT is provided)
    """
    if result_file.content_type != "text/plain":
        return JSONResponse(
            status_code=400, content={"error": "Result file must be a text file"}
        )

    try:
        # Read the content of the result file
        result_content = await result_file.read()
        result_content_str = result_content.decode("utf-8")

        # Parse the AutoDock results
        parsed_data = parse_autodock_results(result_content_str)

        # Generate LLM report
        llm_report = generate_docking_report(parsed_data)

        # Create PDF report
        pdf_report = await create_pdf_report(llm_report)

        # Build response data
        response_data = {
            "pdf_report_base64": io.BytesIO(pdf_report).read().hex(),
            "filename": f"docking_report_{result_file.filename}.pdf",
        }

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)

        temp_file.write(pdf_report)
        temp_file_path = temp_file.name
        temp_file.close()

        # JWT Token for Pinata
        PINATA_JWT_TOKEN = os.getenv("JWT")

        # Upload to Pinata and get the CID
        cid = upload_to_pinata(temp_file_path, PINATA_JWT_TOKEN)
        if not cid:
            raise HTTPException(
                status_code=500, detail="Failed to upload PDF to Pinata"
            )

        # Store the CID on Solana blockchain
        solana_tx = await store_cid_on_solana(cid)
        print(solana_tx)

        # Clean up the temporary file
        os.unlink(temp_file_path)

        # Return the CID along with the PDF file and Solana transaction details
        # response = Response(
        #     content=pdf_report,
        #     media_type="application/pdf",
        #     headers={
        #         "Content-Disposition": f"attachment; filename=docking_report_{file.filename}.pdf",
        #         "X-CID": cid,
        #         "X-Solana-Account": solana_tx["account"],
        #         "X-Solana-Signature": solana_tx["store_signature"]
        #     },
        # )
        response_data["cid"] = cid
        response_data["solana_signature"] = solana_tx.get("store_signature", None)

        # Process visualization data if PDBQT file is provided
        pdbqt_content = await pdbqt_file.read()
        pdbqt_content_str = pdbqt_content.decode("utf-8")

        # Process the PDBQT file and create visualization data
        visualization_data = process_docking_visualization(
            parsed_data, pdbqt_content_str
        )

        # Create data structure for frontend visualization
        frontend_data = create_visualization_data(visualization_data)

        # Add visualization data to response
        response_data["visualization_data"] = frontend_data

        return JSONResponse(status_code=200, content=response_data)

    except Exception as err:
        import traceback

        print(f"Error: {str(err)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=400, detail=f"Error processing docking data: {str(err)}"
        )
