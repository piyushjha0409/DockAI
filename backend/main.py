import io
import tempfile
import os
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Response
from utils.parser import parse_pdb_file, parse_pdbqt_file, read_pdb_to_dataframe
from utils.llm_integration import generate_report_from_parsed_data
from utils.visualization import create_pdb_visualization
from utils.pdf_generator import create_pdf_report
from typing import Optional, List, Dict
from ipfs.pinata_post import upload_to_pinata  # Import the Pinata upload function
from utils.read_to_dataframe import read_pdb_to_dataframe

load_dotenv()
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Application started successfully")


@app.post("/read-pdb-file/")
async def parse_docking_file(file: UploadFile):
    try:
        content = await file.read()
        parsed_data = await parse_pdbqt_file(content)
        
        llm_report = await generate_report_from_parsed_data(parsed_data)
        
        pdf_report = await create_pdf_report(llm_report)

        # Save the PDF to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_file.write(pdf_report)
        temp_file_path = temp_file.name
        temp_file.close()

        # JWT Token for Pinata
        PINATA_JWT_TOKEN = os.getenv("JWT")

        # Upload to Pinata and get the CID
        cid = upload_to_pinata(temp_file_path, PINATA_JWT_TOKEN)
        if not cid:
            raise HTTPException(status_code=500, detail="Failed to upload PDF to Pinata")

        # Clean up the temporary file
        os.unlink(temp_file_path)

        # Return the CID along with the PDF file
        return {
            "cid": cid,
            "pdf_report": Response(
                content=pdf_report,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=docking_report_{file.filename}.pdf"
                }
            )
        }
    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise
    except Exception as err:
        import traceback
        print(f"Error: {str(err)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error processing PDB file: {str(err)}")


@app.post("/visualize-pdb/")
async def visualize_pdb_file(
    file: UploadFile = File(...),
    binding_residues: Optional[List[str]] = None,
    highlight_atoms: Optional[List[str]] = None,
    width: int = 800,
    height: int = 600,
    style: str = "cartoon",
    surface_opacity: float = 0.5,
    background_color: str = "white"
):
    """
    Create and return all visualizations for a PDB file.
    
    Args:
        file: The PDB file to visualize
        binding_residues: List of residue IDs to highlight
        highlight_atoms: List of atom IDs to highlight
        width: Width of the visualization in pixels
        height: Height of the visualization in pixels
        style: Visualization style for 3D view ('cartoon', 'stick', 'sphere', 'line')
        surface_opacity: Opacity of molecular surface (0-1)
        background_color: Background color of the viewer
    
    Returns:
        Dictionary containing all visualization types
    """
    try:
        content = await file.read()
        
        # Generate all visualizations
        visualizations = {}
        
        # Standard visualization
        standard_viz = await create_pdb_visualization(
            pdb_content=content,
            visualization_type="standard",
            width=width,
            height=height,
            style=style,
            surface_opacity=surface_opacity,
            background_color=background_color
        )
        visualizations["standard"] = standard_viz
        
        # Binding site visualization (if binding residues provided)
        if binding_residues:
            binding_viz = await create_pdb_visualization(
                pdb_content=content,
                visualization_type="binding_site",
                binding_residues=binding_residues,
                width=width,
                height=height,
                style=style,
                surface_opacity=surface_opacity,
                background_color=background_color
            )
            visualizations["binding_site"] = binding_viz
        
        # Electrostatic visualization
        electrostatic_viz = await create_pdb_visualization(
            pdb_content=content,
            visualization_type="electrostatic",
            width=width,
            height=height,
            style=style,
            surface_opacity=surface_opacity,
            background_color=background_color
        )
        visualizations["electrostatic"] = electrostatic_viz
        
        # 2D visualization
        viz_2d = await create_pdb_visualization(
            pdb_content=content,
            visualization_type="2d",
            width=width,
            height=height,
            background_color=background_color
        )
        visualizations["2d"] = viz_2d
        
        # Extract structure info from standard visualization
        structure_info = standard_viz.get("structure_info", {})
        
        return {
            "visualizations": visualizations,
            "structure_info": structure_info
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")

@app.post("/analyze-pdb/")
async def analyze_pdb_structure(file: UploadFile = File(...)):
    """
    Analyze a PDB file and return structure information.
    
    Args:
        file: The PDB file to analyze
        
    Returns:
        Structure information as JSON
    """
    try:
        content = await file.read()
        
        # Parse PDB file to DataFrame
        df, header = await read_pdb_to_dataframe(content)
        
        # Get structure statistics
        chains = df['chain_id'].unique().tolist()
        residues = df[['chain_id', 'residue_number', 'residue_name']].drop_duplicates()
        
        # Prepare response
        result = {
            "structure_id": header.get("identifier", "Unknown") if header else "Unknown",
            "title": header.get("title", "Unknown") if header else "Unknown",
            "num_atoms": len(df),
            "num_chains": len(chains),
            "num_residues": len(residues),
            "chains": [{"chain_id": chain, "num_residues": len(residues[residues['chain_id'] == chain])} for chain in chains],
            "header_info": header
        }
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")