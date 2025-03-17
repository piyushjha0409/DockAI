from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException
from Bio.PDB import * 
import io

app = FastAPI()

# GET route 
@app.get("/")
def read_root():
    return {"Hello": "World"}

# POST route for parsing the content of the pdb files 
@app.post("/upload")
async def read_pdb_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        file_like_object = io.StringIO(content.decode('utf-8'))
        
        pdbparser = PDBParser(QUIET=True)
        struct = pdbparser.get_structure("uploaded_structure", file_like_object)
        
        chains_data = []
        residues_data = []
        atoms_data = []
        
        for chain in struct.get_chains():
            chains_data.append({
                "id": chain.id,
                "full_id": chain.full_id
            })
            
        for residue in struct.get_residues():
            residues_data.append({
                "resname": residue.resname,
                "id": residue.id[1],  # Residue number
                "full_id": str(residue.full_id)
            })
            
        for atom in struct.get_atoms():
            atoms_data.append({
                "name": atom.name,
                "element": atom.element,
                "coords": atom.coord.tolist(),  # Convert numpy array to list
                "serial_number": atom.serial_number if hasattr(atom, 'serial_number') else None,
                "full_id": str(atom.full_id)
            })

        return {
            "structure_id": struct.id,
            "num_chains": len(chains_data),
            "num_residues": len(residues_data),
            "num_atoms": len(atoms_data),
            "model_count": len(struct),
            "chains": chains_data,
            "residues": residues_data,
            "atoms": atoms_data
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Error parsing PDB file: {str(err)}") 
        

