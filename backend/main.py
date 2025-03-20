import io
from fastapi import FastAPI, HTTPException, UploadFile, File
import os
from utils.parser import parse_pdb_file
from utils.llm_integration import generate_report_from_parsed_data
from utils.visualization import create_pdb_visualization
from utils.pdf_generator import create_pdf_report
from typing import Optional, List

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")


@app.post("/read-pdb-file/")
async def parse_docking_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parsed_data = await parse_pdb_file(content)
        
        llm_report = await generate_report_from_parsed_data(parsed_data)
        
        pdf_report = await create_pdf_report(llm_report)
        
        return io.BytesIO(pdf_report)
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Error parsing PDB file: {str(err)}")


@app.post("/visualize-pdb/")
async def visualize_pdb_file(
    file: UploadFile = File(...),
    visualization_type: str = "standard",
    binding_residues: Optional[List[str]] = None,
    highlight_atoms: Optional[List[str]] = None,
    width: int = 800,
    height: int = 600,
    style: str = "cartoon",
    surface_opacity: float = 0.5,
    background_color: str = "white"
):
    """
    Create and return a visualization for a PDB file.
    
    Args:
        file: The PDB file to visualize
        visualization_type: Type of visualization to create
            - "standard": Basic 3D representation
            - "binding_site": Highlighting binding residues
            - "2d": 2D representation
            - "electrostatic": Electrostatic surface
        binding_residues: List of residue IDs to highlight (for binding_site mode)
        highlight_atoms: List of atom IDs to highlight
        width: Width of the visualization in pixels
        height: Height of the visualization in pixels
        style: Visualization style ('cartoon', 'stick', 'sphere', 'line')
        surface_opacity: Opacity of molecular surface (0-1)
        background_color: Background color of the viewer
    
    Returns:
        Visualization result (HTML content or base64 encoded image)
    """
    try:
        content = await file.read()
        
        visualization = await create_pdb_visualization(
            pdb_content=content,
            visualization_type=visualization_type,
            binding_residues=binding_residues,
            highlight_atoms=highlight_atoms,
            width=width,
            height=height,
            style=style,
            surface_opacity=surface_opacity,
            background_color=background_color
        )
        
        return visualization
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")


# @app.get("/generate_docking_report/{file_id}")
# async def generate_docking_report(file_id: int): 
#     """
#     Generate a PDF report for a given uploaded PDB file

#     Arguments: 
#         file_id: ID of the uploaded PDB file

#     Returns: 
#         PDF file response
#     """

#     file_record = await UplaodedFile.get_or_none(id=file_id)
#     if not file_record:
#         raise HTTPException(status_code=404, detail="File not found")

#     file_path = file_record.file_path


#     # Check if the file exists 

#     if not os.path.exists(file_path): 
#         raise HTTPException(status_code=404, detail="File not found at disk")

#     try: 

#         #Read file content 
#         async with aiofiles.   