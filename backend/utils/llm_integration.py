import datetime
import logging
from typing import Any, Dict, List

import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_docking_report(docking_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a report analyzing docking results.

    Args:
        docking_results: List of dictionaries containing docking mode information
                        (mode, affinity, rmsd_lb, rmsd_ub)

    Returns:
        Dictionary containing the structured report
    """
    try:
        # Initialize the Gemini model
        api_key = "AIzaSyBzRAnoVD7l3yGOWYJhBdd4MB6pePx7DYs"  # Add your API key here
        if not api_key:
            logger.error("No Google API key provided")
            return {"error": "API key is required", "status": "failed"}

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-002")

        # Format the docking results for the prompt
        docking_details = "## Docking Results:\n"
        for result in docking_results:
            mode = result.get("mode", "N/A")
            affinity = result.get("affinity", "N/A")
            rmsd_lb = result.get("rmsd_lb", "N/A")
            rmsd_ub = result.get("rmsd_ub", "N/A")

            docking_details += f"- Mode {mode}:\n"
            docking_details += f"  - Binding Affinity: {affinity} kcal/mol\n"
            docking_details += f"  - RMSD Lower Bound: {rmsd_lb}\n"
            docking_details += f"  - RMSD Upper Bound: {rmsd_ub}\n"

        # Create the prompt for analysis
        prompt = f"""
        As a pharmaceutical analysis expert, generate a detailed report on the molecular docking results provided.
        
        {docking_details}
        
        Please analyze these docking results and provide:
        1. An executive summary of the docking results, highlighting the best binding modes
        2. Detailed analysis of binding affinities across all modes, including discussion of the energetics
        3. Evaluation of potential drug efficacy based on binding affinities, with particular attention to the modes with strongest binding
        4. Analysis of RMSD values and what they indicate about binding site preferences
        5. Recommendations for further optimization based on the observed binding patterns
        
        Format the report with clear headings and subheadings for inclusion in a scientific document.
        Use tables and comparative analysis where appropriate.
        """

        # Generate content with Gemini
        response = model.generate_content(prompt)

        # Extract metrics for the report
        binding_affinities = [
            result["affinity"] for result in docking_results if "affinity" in result
        ]
        best_affinity = min(binding_affinities) if binding_affinities else None
        best_mode = next(
            (r["mode"] for r in docking_results if r.get("affinity") == best_affinity),
            None,
        )

        # Create structured report
        structured_report = {
            "raw_report": response.text,
            "best_binding_mode": best_mode,
            "best_affinity": best_affinity,
            "all_affinities": binding_affinities,
            "docking_results": docking_results,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "success",
        }

        logger.info("Successfully generated docking analysis report")
        return structured_report

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {"error": str(e), "status": "failed"}
