import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
import aiofiles
import os
from models import UploadedFile
from database import init_db
import Bio.PDB

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup():
    await init_db()
    print("Database initialized")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    db_entry = await UploadedFile.create(filename=file.filename, file_path=file_location)
    
    return {"message": "File uploaded", "file_id": db_entry.id, "filename": db_entry.filename}


@app.post("/read-pdb-file/")
async def read_pdb_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        file_like_object = io.StringIO(content.decode('utf-8'))
        
        pdbparser = Bio.PDB.PDBParser(QUIET=True)
        struct = pdbparser.get_structure("uploaded_structure", file_like_object)
        
        model_data = []
        chains_data = []
        residues_data = []
        atoms_data = []

        for model in struct.get_models():
            for chain in model.get_chains():
                print(chain)
            model_data.append({
                "id": model.id,
                "serial_num": model.serial_num
            })
        
        for chain in struct.get_chains():
            print(chain)
            chains_data.append({
                "id": chain.id,
                "full_id": chain.full_id
            })
            
        for residue in struct.get_residues():
            residues_data.append({
                "resname": residue.resname,
                "id": residue.id[1],
                "full_id": str(residue.full_id)
            })
            
        for atom in struct.get_atoms():
            atoms_data.append({
                "name": atom.name,
                "element": atom.element,
                "coords": atom.coord.tolist(),
                "serial_number": atom.serial_number if hasattr(atom, 'serial_number') else None,
                "full_id": str(atom.full_id)
            })

        return {
            "structure_id": struct.id,
            "num_chains": len(chains_data),
            "num_residues": len(residues_data),
            "num_atoms": len(atoms_data),
            "model_count": len(struct),
            "models": model_data,
            "chains": chains_data,
            "residues": residues_data,
            "atoms": atoms_data
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Error parsing PDB file: {str(err)}")