import io 
import Bio.PDB
from typing import Dict, Any, Union, IO
from fastapi import HTTPException
import io 
from biopandas.pdb import PandasPdb
from prody import parsePDBHeader
from typing import Optional, Tuple, Dict, Any, Union
import pandas as pd
import io
import os

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
                model_data.append({
                    "id": model.id,
                    "serial_num": model.serial_num
                })
        
        for chain in struct.get_chains():
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

async def parse_pdbqt_file(file_content: Union[str, bytes, IO]) -> Dict[str, Any]:
    """
    Parse PDBQT file from docking software like AutoDock Vina.
    Extracts both structural data and docking scores.
    """
    try:
        # Convert content to string
        if isinstance(file_content, bytes):
            content_str = file_content.decode('utf-8')
        elif isinstance(file_content, str):
            content_str = file_content
        else:
            # Read file-like object
            content_str = file_content.read()
            if isinstance(content_str, bytes):
                content_str = content_str.decode('utf-8')
        
        # First, extract docking information from REMARKS
        docking_scores = []
        models = []
        current_model = None
        
        lines = content_str.split('\n')
        
        # Extract binding affinities from REMARK lines
        for line in lines:
            if line.startswith("REMARK VINA RESULT:"):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        affinity = float(parts[3])
                        rmsd_lb = float(parts[4])
                        rmsd_ub = float(parts[5]) if len(parts) > 5 else 0.0
                        
                        docking_scores.append({
                            "docking_score": affinity,
                            "binding_energy": affinity,  # Same in Vina
                            "rmsd_lb": rmsd_lb,
                            "rmsd_ub": rmsd_ub
                        })
                    except (ValueError, IndexError):
                        pass
            
            # Track MODEL sections
            elif line.startswith("MODEL"):
                if current_model:
                    models.append(current_model)
                try:
                    model_num = int(line.split()[1])
                    current_model = {"model_num": model_num, "atoms": []}
                except (ValueError, IndexError):
                    current_model = {"model_num": len(models) + 1, "atoms": []}
            
            # Add atoms to current model
            elif line.startswith("ATOM") or line.startswith("HETATM"):
                if current_model:
                    current_model["atoms"].append(line)
        
        # Don't forget the last model
        if current_model:
            models.append(current_model)
        
        # Now use BioPython to parse the structural part (this handles the 3D coordinates)
        file_like_object = io.StringIO(content_str)
        pdbparser = Bio.PDB.PDBParser(QUIET=True)
        
        try:
            struct = pdbparser.get_structure("uploaded_structure", file_like_object)
            
            model_data = []
            chains_data = []
            residues_data = []
            atoms_data = []
            ligands = []

            # Extract basic structure info
            for model in struct.get_models():
                model_data.append({
                    "id": model.id,
                    "serial_num": model.serial_num
                })
            
            # Identify chains
            for chain in struct.get_chains():
                chains_data.append({
                    "id": chain.id,
                    "full_id": chain.full_id
                })
            
            # Extract residues - note special handling for HETATM records
            ligand_residues = []
            for residue in struct.get_residues():
                residue_info = {
                    "resname": residue.resname,
                    "id": residue.id[1],
                    "full_id": str(residue.full_id)
                }
                
                residues_data.append(residue_info)
                
                # Check if this is a ligand (non-standard amino acid or nucleotide)
                if residue.id[0].strip() and residue.id[0] != ' ':
                    ligand_residues.append(residue_info)
            
            # Process atoms
            for atom in struct.get_atoms():
                atoms_data.append({
                    "name": atom.name,
                    "element": atom.element,
                    "coords": atom.coord.tolist(),
                    "serial_number": atom.serial_number if hasattr(atom, 'serial_number') else None,
                    "full_id": str(atom.full_id)
                })
            
            # Group ligand residues that are the same chemical entity
            if ligand_residues:
                # For simplicity, we'll treat each hetero residue as a separate ligand
                for ligand_res in ligand_residues:
                    ligands.append({
                        "name": ligand_res["resname"],
                        "residue_id": ligand_res["id"],
                        "full_id": ligand_res["full_id"]
                    })
            
            # Build interactions from the docking scores
            interactions = []
            for i, score in enumerate(docking_scores):
                interaction = {
                    "mode": i + 1,
                    "docking_score": score["docking_score"],
                    "binding_energy": score["binding_energy"],
                    "rmsd_lb": score["rmsd_lb"],
                    "rmsd_ub": score["rmsd_ub"]
                }
                interactions.append(interaction)
            
            # Build the final result
            return {
                "structure_id": struct.id,
                "num_chains": len(chains_data),
                "num_residues": len(residues_data),
                "num_atoms": len(atoms_data),
                "model_count": len(struct),
                "models": model_data,
                "chains": chains_data,
                "residues": residues_data,
                "atoms": atoms_data,
                "ligands": ligands,
                "docking_scores": docking_scores,
                "interactions": interactions,
                "is_docking_result": True,
                "binding_energies": [score["binding_energy"] for score in docking_scores],
                "chain_count": len(chains_data),
                "ligand_count": len(ligands)
            }
        
        except Exception as bio_err:
            # If BioPython parser fails, still return docking information
            return {
                "structure_id": "uploaded_structure",
                "docking_scores": docking_scores,
                "interactions": [{
                    "mode": i + 1,
                    "docking_score": score["docking_score"],
                    "binding_energy": score["binding_energy"],
                    "rmsd_lb": score["rmsd_lb"],
                    "rmsd_ub": score["rmsd_ub"]
                } for i, score in enumerate(docking_scores)],
                "is_docking_result": True,
                "binding_energies": [score["binding_energy"] for score in docking_scores],
                "model_count": len(models),
                "error_parsing_structure": str(bio_err)
            }
    
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Error parsing PDBQT file: {str(err)}")