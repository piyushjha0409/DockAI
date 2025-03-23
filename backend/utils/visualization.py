import re
from typing import Dict, List, Any

def parse_pdbqt_models(pdbqt_content: str) -> List[Dict[str, Any]]:
    """
    Parse the PDBQT file content to extract models, their binding affinities,
    and atomic coordinates.
    
    Args:
        pdbqt_content: Content of the PDBQT file as a string
        
    Returns:
        List of dictionaries containing model data
    """
    models = []
    current_model = None
    
    for line in pdbqt_content.split('\n'):
        if line.startswith('MODEL'):
            if current_model:
                models.append(current_model)
            model_num = int(line.split()[1])
            current_model = {
                'model_id': model_num,
                'binding_affinity': None,
                'atoms': [],
                'bonds': []
            }
        
        elif line.startswith('REMARK VINA RESULT:') and current_model:
            parts = line.split()
            current_model['binding_affinity'] = float(parts[3])
            
        elif line.startswith('ATOM') and current_model:
            # Parse atom data from PDBQT format
            atom_id = int(line[6:11].strip())
            atom_name = line[12:16].strip()
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            
            current_model['atoms'].append({
                'id': atom_id,
                'name': atom_name,
                'x': x,
                'y': y,
                'z': z,
                'element': atom_name[0] if not atom_name[0].isdigit() else atom_name[1]
            })
    
    # Add the last model
    if current_model:
        models.append(current_model)
    
    # Add simple bond information (this is simplified - real implementation would need more chemistry knowledge)
    for model in models:
        _add_bond_information(model)
    
    return models

def _add_bond_information(model: Dict[str, Any]) -> None:
    """
    Add simple bond information to the model based on atomic distances.
    This is a simplified approach - a real implementation would use more
    sophisticated chemical bond determination.
    
    Args:
        model: The model data dictionary to update with bond information
    """
    atoms = model['atoms']
    bonds = []
    
    # Simple distance-based bond detection (very simplistic)
    for i, atom1 in enumerate(atoms):
        for j, atom2 in enumerate(atoms[i+1:], i+1):
            # Calculate distance between atoms
            dx = atom1['x'] - atom2['x']
            dy = atom1['y'] - atom2['y']
            dz = atom1['z'] - atom2['z']
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            # If atoms are close enough, consider them bonded
            # This is a very simplified approach
            if distance < 2.0:  # Typical bond length in Angstroms
                bonds.append({
                    'atom1': atom1['id'],
                    'atom2': atom2['id'],
                    'order': 1  # Assuming single bonds for simplicity
                })
    
    model['bonds'] = bonds

def process_docking_visualization(parsed_results: Dict, pdbqt_content: str) -> Dict[str, Any]:
    """
    Process the docking results and PDBQT file to create visualization data.
    
    Args:
        parsed_results: Parsed results from the AutoDock output
        pdbqt_content: Content of the PDBQT file as a string
        
    Returns:
        Dictionary containing data needed for visualization
    """
    # Parse the PDBQT models
    models = parse_pdbqt_models(pdbqt_content)
    
    # Combine with the parsed results
    return {
        'results': parsed_results,
        'models': models
    }

def create_visualization_data(visualization_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a structured data format for the frontend visualization.
    
    Args:
        visualization_data: Processed visualization data
        
    Returns:
        Dictionary formatted for frontend visualization libraries
    """
    models = visualization_data['models']
    results = visualization_data['results']
    
    # Sort models by binding affinity (best first)
    sorted_models = sorted(models, key=lambda x: x['binding_affinity'])
    
    # Create the response structure
    frontend_data = {
        'models': [],
        'summary': {
            'best_binding_affinity': sorted_models[0]['binding_affinity'] if sorted_models else None,
            'model_count': len(models),
            'binding_energies': [model['binding_affinity'] for model in sorted_models]
        }
    }
    
    # Format each model for the frontend
    for model in sorted_models:
        frontend_data['models'].append({
            'model_id': model['model_id'],
            'binding_affinity': model['binding_affinity'],
            'atom_count': len(model['atoms']),
            'atoms': model['atoms'],
            'bonds': model['bonds']
        })
    
    return frontend_data
