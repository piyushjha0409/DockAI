import io 
import Bio.PDB
from typing import Dict, Any, Union, IO
from fastapi import HTTPException

async def parse_pdb_file(file_content: Union[str, bytes, IO]) -> Dict[str, Any]:
    try:
        if isinstance(file_content, bytes):
            file_like_object = io.StringIO(file_content.decode('utf-8'))
        elif isinstance(file_content, str):
            file_like_object = io.StringIO(file_content)
        else:
            file_like_object = file_content
            
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
