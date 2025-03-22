import io
import base64
import matplotlib.pyplot as plt
from Bio.PDB import PDBParser
import py3Dmol
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
import plotly.express as px
import plotly.graph_objects as go
from .parser import read_pdb_to_dataframe
import json

class MolecularVisualizer:
    """Class for visualizing molecular structures from PDB files."""
    
    @staticmethod
    def create_interactive_view(pdb_content: Union[str, bytes], 
                               width: int = 800, 
                               height: int = 600,
                               style: str = "cartoon",
                               surface_opacity: float = 0.5,
                               background_color: str = "white") -> str:
        """
        Create interactive 3D visualization of a molecule using py3Dmol.
        
        Args:
            pdb_content: PDB file content as string or bytes
            width: Viewer width in pixels
            height: Viewer height in pixels
            style: Visualization style ('cartoon', 'stick', 'sphere', 'line')
            surface_opacity: Opacity of molecular surface (0-1)
            background_color: Background color of the viewer
            
        Returns:
            HTML string containing an interactive 3D visualization
        """
        if isinstance(pdb_content, bytes):
            pdb_content = pdb_content.decode('utf-8')
            
        # Create a py3Dmol view
        view = py3Dmol.view(width=width, height=height)
        view.addModel(pdb_content, 'pdb')
        
        # Apply the requested style
        if style == 'cartoon':
            view.setStyle({'cartoon': {'color': 'spectrum'}})
        elif style == 'stick':
            view.setStyle({'stick': {}})
        elif style == 'sphere':
            view.setStyle({'sphere': {}})
        elif style == 'line':
            view.setStyle({'line': {}})
        else:
            # Default to cartoon if invalid style
            view.setStyle({'cartoon': {'color': 'spectrum'}})
        
        # Add a transparent surface
        view.addSurface(py3Dmol.VDW, {'opacity': surface_opacity})
        
        # Set other viewing options
        view.setBackgroundColor(background_color)
        view.zoomTo()
        
        # Get the HTML representation
        html_content = view._make_html()
        
        return html_content
    
    @staticmethod
    def highlight_binding_site(pdb_content: Union[str, bytes], 
                              binding_residues: List[str],
                              width: int = 800, 
                              height: int = 600) -> str:
        """
        Create visualization highlighting specific binding residues.
        
        Args:
            pdb_content: PDB file content as string or bytes
            binding_residues: List of residue IDs to highlight (e.g., ['A:45', 'A:46'])
            width: Viewer width in pixels
            height: Viewer height in pixels
            
        Returns:
            HTML string containing visualization with highlighted binding site
        """
        if isinstance(pdb_content, bytes):
            pdb_content = pdb_content.decode('utf-8')
            
        view = py3Dmol.view(width=width, height=height)
        view.addModel(pdb_content, 'pdb')
        
        # Set default style for the whole protein
        view.setStyle({'cartoon': {'color': 'lightgray'}})
        
        # Highlight binding residues
        selector = {'resi': binding_residues}
        view.addStyle(selector, {'stick': {'colorscheme': 'greenCarbon', 'radius': 0.2}})
        view.addSurface(py3Dmol.VDW, {'opacity': 0.7, 'colorscheme': 'whiteCarbon'}, selector)
        
        # Add labels to binding residues
        for residue in binding_residues:
            view.addLabel(residue, {'font': 'Arial', 'fontSize': 12, 'fontColor': 'black', 'backgroundOpacity': 0.7})
        
        view.zoomTo(selector)
        
        return view._make_html()
    
    @staticmethod
    def visualize_protein_ligand_interaction(protein_pdb: Union[str, bytes], 
                                           ligand_pdb: Union[str, bytes],
                                           width: int = 800, 
                                           height: int = 600) -> str:
        """
        Visualize interaction between protein and ligand.
        
        Args:
            protein_pdb: PDB content of the protein
            ligand_pdb: PDB content of the ligand
            width: Viewer width in pixels
            height: Viewer height in pixels
            
        Returns:
            HTML string containing visualization of protein-ligand interaction
        """
        if isinstance(protein_pdb, bytes):
            protein_pdb = protein_pdb.decode('utf-8')
        if isinstance(ligand_pdb, bytes):
            ligand_pdb = ligand_pdb.decode('utf-8')
            
        view = py3Dmol.view(width=width, height=height)
        
        # Add protein
        view.addModel(protein_pdb, 'pdb', {'model': 'protein'})
        view.setStyle({'model': 'protein'}, {'cartoon': {'color': 'spectrum'}})
        
        # Add ligand
        view.addModel(ligand_pdb, 'pdb', {'model': 'ligand'})
        view.setStyle({'model': 'ligand'}, {'stick': {'colorscheme': 'cyanCarbon', 'radius': 0.2}})
        
        # Calculate and show interactions
        view.addSurface(py3Dmol.VDW, {'opacity': 0.5, 'color': 'white'}, {'model': 'protein'})
        
        # Add distance measurement between closest atoms
        view.addResLabels({'model': 'protein', 'within': {'distance': 4, 'sel': {'model': 'ligand'}}})
        
        # Zoom to the ligand and surrounding protein residues
        view.zoomTo({'model': 'ligand'}, 1000)  # Zoom with some padding
        
        return view._make_html()
    
    @staticmethod
    def generate_2d_representation(pdb_content: Union[str, bytes], 
                                 highlight_residues: Optional[List[str]] = None) -> str:
        """
        Generate a 2D representation of the molecular structure as a base64 encoded PNG.
        
        Args:
            pdb_content: PDB file content as string or bytes
            highlight_residues: Optional list of residue IDs to highlight
            
        Returns:
            Base64 encoded PNG image string
        """
        try:
            # Convert PDB to RDKit molecule
            # Note: This is approximate, as RDKit doesn't natively support PDB well for complex proteins
            # For real applications, you might need OpenBabel or other tools
            if isinstance(pdb_content, bytes):
                pdb_content = pdb_content.decode('utf-8')
            
            # For this example, we'll extract HETATM records which often contain smaller molecules
            # This is a simplified approach and may not work for all PDB files
            lines = pdb_content.split('\n')
            hetatm_lines = [line for line in lines if line.startswith('HETATM')]
            
            # If no small molecules are found, create a simple representation of amino acids
            if not hetatm_lines:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("protein", io.StringIO(pdb_content))
                
                # Create a simple 2D plot showing Cα atoms
                plt.figure(figsize=(10, 8))
                
                # Extract Cα coordinates
                x_coords = []
                y_coords = []
                labels = []
                
                for residue in structure.get_residues():
                    if 'CA' in residue:
                        ca_atom = residue['CA']
                        x_coords.append(ca_atom.coord[0])
                        y_coords.append(ca_atom.coord[1])
                        labels.append(f"{residue.resname}{residue.id[1]}")
                
                # Plot basic structure
                plt.scatter(x_coords, y_coords, s=50, c='blue', alpha=0.7)
                
                # Highlight specific residues if requested
                if highlight_residues:
                    highlight_indices = []
                    for i, label in enumerate(labels):
                        if any(res in label for res in highlight_residues):
                            highlight_indices.append(i)
                    
                    if highlight_indices:
                        highlighted_x = [x_coords[i] for i in highlight_indices]
                        highlighted_y = [y_coords[i] for i in highlight_indices]
                        plt.scatter(highlighted_x, highlighted_y, s=100, c='red', edgecolors='black')
                
                # Add labels for residues
                for i, label in enumerate(labels):
                    plt.annotate(label, (x_coords[i], y_coords[i]), fontsize=6)
                
                plt.title('2D Representation of Protein Backbone (Cα atoms)')
                plt.xlabel('X coordinate (Å)')
                plt.ylabel('Y coordinate (Å)')
                plt.grid(True, alpha=0.3)
                
                # Save plot to a bytes buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100)
                buf.seek(0)
                
                # Convert to base64
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()
                
                return img_base64
            
            # If HETATM records are found, try to create a proper 2D molecular representation
            # (This part would need improvement for real applications)
            mol = Chem.MolFromPDBBlock(pdb_content)
            
            if mol is None:
                raise ValueError("Could not convert PDB to RDKit molecule")
                
            # Generate 2D coordinates
            AllChem.Compute2DCoords(mol)
            
            # Draw the molecule
            img = Draw.MolToImage(mol, size=(800, 600))
            
            # Convert PIL image to base64
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            # Fallback: Create a simple text-based image stating the error
            plt.figure(figsize=(6, 3))
            plt.text(0.5, 0.5, f"Could not generate 2D representation: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return img_base64
    
    @staticmethod
    def electrostatic_surface_visualization(pdb_content: Union[str, bytes],
                                          width: int = 800,
                                          height: int = 600) -> str:
        """
        Create visualization with electrostatic surface coloring.
        
        Args:
            pdb_content: PDB file content as string or bytes
            width: Viewer width in pixels
            height: Viewer height in pixels
            
        Returns:
            HTML string containing visualization with electrostatic surface
        """
        if isinstance(pdb_content, bytes):
            pdb_content = pdb_content.decode('utf-8')
            
        view = py3Dmol.view(width=width, height=height)
        view.addModel(pdb_content, 'pdb')
        
        # Basic cartoon representation
        view.setStyle({'cartoon': {'colorscheme': 'chain'}})
        
        # Add electrostatic surface - py3Dmol approximates this with atom coloring
        view.addSurface(py3Dmol.VDW, {
            'opacity': 0.85,
            'colorscheme': {
                'prop': 'partialCharge',
                'gradient': 'rwb',  # red-white-blue gradient for negative to positive charge
                'min': -0.5,
                'max': 0.5
            }
        })
        
        view.zoomTo()
        
        return view._make_html()

# Function to be used in FastAPI routes
async def create_pdb_visualization(pdb_content: Union[str, bytes], 
                                 visualization_type: str = "standard",
                                 binding_residues: Optional[List[str]] = None,
                                 ligand_pdb: Optional[Union[str, bytes]] = None,
                                 **kwargs) -> Dict[str, Any]:
    """
    Create visualization for PDB file based on specified type.
    
    Args:
        pdb_content: PDB file content as string or bytes
        visualization_type: Type of visualization to create
            - "standard": Basic 3D representation
            - "binding_site": Highlighting binding residues
            - "protein_ligand": Protein-ligand interaction
            - "2d": 2D representation
            - "electrostatic": Electrostatic surface
        binding_residues: List of residue IDs to highlight (for binding_site mode)
        ligand_pdb: PDB content of ligand (for protein_ligand mode)
        **kwargs: Additional parameters for visualization
        
    Returns:
        Dictionary with visualization data and metadata
    """
    visualizer = MolecularVisualizer()
    
    # Set default width and height if not provided
    width = kwargs.get('width', 800)
    height = kwargs.get('height', 600)
    
    if visualization_type == "standard":
        style = kwargs.get('style', 'cartoon')
        surface_opacity = kwargs.get('surface_opacity', 0.5)
        background_color = kwargs.get('background_color', 'white')
        
        html_content = visualizer.create_interactive_view(
            pdb_content, width, height, style, surface_opacity, background_color
        )
        
        return {
            "type": "html",
            "content": html_content,
            "visualization_type": "standard_3d"
        }
        
    elif visualization_type == "binding_site":
        if not binding_residues:
            raise ValueError("binding_residues must be provided for binding_site visualization")
        
        html_content = visualizer.highlight_binding_site(
            pdb_content, binding_residues, width, height
        )
        
        return {
            "type": "html",
            "content": html_content,
            "visualization_type": "binding_site",
            "highlighted_residues": binding_residues
        }
        
    elif visualization_type == "protein_ligand":
        if not ligand_pdb:
            raise ValueError("ligand_pdb must be provided for protein_ligand visualization")
        
        html_content = visualizer.visualize_protein_ligand_interaction(
            pdb_content, ligand_pdb, width, height
        )
        
        return {
            "type": "html",
            "content": html_content,
            "visualization_type": "protein_ligand_interaction"
        }
        
    elif visualization_type == "2d":
        image_base64 = visualizer.generate_2d_representation(
            pdb_content, binding_residues
        )
        
        return {
            "type": "image",
            "content": image_base64,
            "visualization_type": "2d_representation",
            "format": "png",
            "encoding": "base64"
        }
        
    elif visualization_type == "electrostatic":
        html_content = visualizer.electrostatic_surface_visualization(
            pdb_content, width, height
        )
        
        return {
            "type": "html",
            "content": html_content,
            "visualization_type": "electrostatic_surface"
        }
        
    else:
        raise ValueError(f"Unsupported visualization type: {visualization_type}")

async def create_pdb_visualization(
    pdb_content: bytes,
    visualization_type: str = "standard",
    binding_residues: Optional[List[str]] = None,
    highlight_atoms: Optional[List[str]] = None,
    width: int = 800,
    height: int = 600,
    style: str = "cartoon",
    surface_opacity: float = 0.5,
    background_color: str = "white"
) -> Dict[str, Any]:
    """
    Create a visualization of a PDB structure.
    
    Args:
        pdb_content (bytes): PDB file content
        visualization_type (str): Type of visualization
        binding_residues (List[str], optional): Residues to highlight
        highlight_atoms (List[str], optional): Atoms to highlight
        width (int): Width of visualization
        height (int): Height of visualization
        style (str): Visualization style
        surface_opacity (float): Surface opacity
        background_color (str): Background color
        
    Returns:
        Dict[str, Any]: Visualization data with HTML content
    """
    try:
        # Parse PDB file to DataFrame
        df, header = await read_pdb_to_dataframe(pdb_content)
        
        # Create base figure
        if visualization_type == "standard":
            fig = px.scatter_3d(
                df, 
                x='x_coord', 
                y='y_coord', 
                z='z_coord', 
                color='element_symbol',
                hover_data=['atom_name', 'residue_name', 'chain_id', 'residue_number'],
                title=f"PDB Structure Visualization"
            )
            fig.update_traces(marker_size=4)
            
        elif visualization_type == "binding_site":
            # Filter for binding residues if provided
            if binding_residues:
                binding_mask = df['chain_id'] + ':' + df['residue_number'].astype(str)
                binding_mask = binding_mask.isin(binding_residues)
                
                # Create a color column
                df['color'] = 'Other'
                df.loc[binding_mask, 'color'] = 'Binding Site'
                
                fig = px.scatter_3d(
                    df, 
                    x='x_coord', 
                    y='y_coord', 
                    z='z_coord', 
                    color='color',
                    color_discrete_map={'Binding Site': 'red', 'Other': 'lightgrey'},
                    hover_data=['atom_name', 'residue_name', 'chain_id', 'residue_number'],
                    title=f"Binding Site Visualization"
                )
                fig.update_traces(marker_size=4)
            else:
                fig = px.scatter_3d(
                    df, 
                    x='x_coord', 
                    y='y_coord', 
                    z='z_coord', 
                    color='element_symbol',
                    hover_data=['atom_name', 'residue_name', 'chain_id', 'residue_number'],
                    title=f"PDB Structure Visualization"
                )
                fig.update_traces(marker_size=4)
                
        elif visualization_type == "electrostatic":
            # Use element charge as proxy for electrostatic potential
            charge_map = {
                'O': -0.5,   # Oxygen (negative)
                'N': -0.5,   # Nitrogen (negative)
                'S': -0.3,   # Sulfur (slightly negative)
                'P': -0.3,   # Phosphorus (slightly negative)
                'C': 0.0,    # Carbon (neutral)
                'H': 0.1,    # Hydrogen (slightly positive)
                'MG': 2.0,   # Magnesium (positive)
                'CA': 2.0,   # Calcium (positive)
                'ZN': 2.0,   # Zinc (positive)
                'FE': 2.0,   # Iron (positive)
            }
            
            # Apply charge map (default to 0 for unknown elements)
            df['charge'] = df['element_symbol'].map(lambda x: charge_map.get(x, 0))
            
            fig = px.scatter_3d(
                df, 
                x='x_coord', 
                y='y_coord', 
                z='z_coord', 
                color='charge',
                color_continuous_scale='RdBu_r',  # Blue negative, Red positive
                hover_data=['atom_name', 'residue_name', 'chain_id', 'residue_number'],
                title=f"Electrostatic Visualization"
            )
            fig.update_traces(marker_size=4)
            
        elif visualization_type == "2d":
            # For 2D visualization, we'll use a 2D projection of the 3D structure
            # Extract alpha carbon atoms for a simpler representation
            ca_atoms = df[df['atom_name'] == 'CA']
            
            fig = px.scatter(
                ca_atoms, 
                x='x_coord', 
                y='y_coord', 
                color='chain_id',
                hover_data=['residue_name', 'residue_number'],
                title=f"2D Projection (X-Y Plane)"
            )
        
        # Update layout
        fig.update_layout(
            width=width,
            height=height,
            paper_bgcolor=background_color,
            plot_bgcolor=background_color,
            scene=dict(
                xaxis=dict(backgroundcolor=background_color),
                yaxis=dict(backgroundcolor=background_color),
                zaxis=dict(backgroundcolor=background_color),
            ) if visualization_type != "2d" else None
        )
        
        # Convert to HTML
        html_content = fig.to_html(include_plotlyjs=True, full_html=False)
        
        # Return visualization data
        return {
            "type": "html",
            "content": html_content,
            "visualization_type": visualization_type,
            "structure_info": {
                "title": header.get("title", "Unknown") if header else "Unknown",
                "pdb_id": header.get("identifier", "Unknown") if header else "Unknown",
                "chains": len(df['chain_id'].unique()),
                "residues": len(df[['chain_id', 'residue_number']].drop_duplicates()),
                "atoms": len(df)
            }
        }
        
    except Exception as e:
        raise ValueError(f"Error creating visualization: {str(e)}")