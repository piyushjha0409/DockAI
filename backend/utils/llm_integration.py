import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import json
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_report_from_parsed_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive report from already parsed PDB data using Gemini Flash 2.0.
    
    Args:
        parsed_data: Dictionary containing parsed structural and binding data from a PDB file
        
    Returns:
        Dictionary containing the structured report ready for PDF generation
    """
    try:
        # Initialize the Gemini model
        api_key = "AIzaSyBzRAnoVD7l3yGOWYJhBdd4MB6pePx7DYs"
        if not api_key:
            logger.error("No Google API key provided. Set GOOGLE_API_KEY environment variable.")
            return {"error": "API key is required", "status": "failed"}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-flash-2.0')
        
        # Prepare the prompt with parsed data
        prompt = _create_analysis_prompt(parsed_data)
        
        # Generate content with Gemini
        response = model.generate_content(prompt)
        
        # Structure the response into a report
        structured_report = _structure_gemini_response(response.text, parsed_data)
        
        logger.info(f"Successfully generated report for structure {parsed_data.get('structure_id', 'unknown')}")
        return structured_report
        
    except GoogleAPIError as e:
        logger.error(f"Gemini API error: {str(e)}")
        return {"error": str(e), "status": "failed"}
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {"error": str(e), "status": "failed"}

def _create_analysis_prompt(data: Dict[str, Any]) -> str:
    """Create a detailed prompt for the Gemini model based on the parsed data."""
    
    # Extract key information
    structure_id = data.get('structure_id', 'Unknown')
    ligands = data.get('ligands', [])
    ligand_names = [lig.get('name', 'Unknown') for lig in ligands]
    interactions = data.get('interactions', [])
    
    # Extract chains information
    chains = data.get('chains', [])
    chain_count = len(chains)
    
    # Create the prompt
    prompt = f"""
    As a pharmaceutical analysis expert, generate a detailed report on the molecular docking results for protein-ligand complex {structure_id}.
    
    ## Structure Information:
    - Structure ID: {structure_id}
    - Number of chains: {chain_count}
    - Ligands present: {', '.join(ligand_names) if ligand_names else 'None detected'}
    
    ## Docking Results:
    {json.dumps(interactions, indent=2)}
    
    Please analyze these results and provide:
    1. An executive summary of the docking results
    2. Detailed analysis of binding affinities and interaction patterns
    3. Evaluation of potential drug efficacy based on binding efficiencies
    4. Comparison with typical values for successful drugs in this class
    5. Recommendations for optimization if applicable
    
    Format the report with clear headings and subheadings for inclusion in a scientific document.
    """
    return prompt

def _structure_gemini_response(response_text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Structure the raw LLM response into a formatted report."""
    import datetime
    
    # Extract available metrics from parsed data
    docking_scores = []
    binding_energies = []
    
    for interaction in parsed_data.get('interactions', []):
        if 'docking_score' in interaction:
            docking_scores.append(interaction['docking_score'])
        if 'binding_energy' in interaction:
            binding_energies.append(interaction['binding_energy'])
    
    # Create structured report
    structured_report = {
        "structure_id": parsed_data.get('structure_id', 'Unknown'),
        "raw_report": response_text,
        "summary": "",  # Would parse from response_text in a more complete implementation
        "binding_analysis": "",  # Would parse from response_text in a more complete implementation
        "efficacy_evaluation": "",  # Would parse from response_text in a more complete implementation
        "comparison": "",  # Would parse from response_text in a more complete implementation
        "recommendations": "",  # Would parse from response_text in a more complete implementation
        "docking_scores": docking_scores,
        "binding_energies": binding_energies,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "success"
    }
    
    # Add metadata to facilitate PDF generation
    structured_report["has_ligands"] = len(parsed_data.get('ligands', [])) > 0
    structured_report["ligand_count"] = len(parsed_data.get('ligands', []))
    structured_report["chain_count"] = len(parsed_data.get('chains', []))
    
    return structured_report