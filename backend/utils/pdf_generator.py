from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from typing import Dict, Any, Optional
import io
import os
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def create_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """
    Create a PDF report from the structured data returned by the LLM.
    
    Args:
        report_data: Dictionary containing the structured report data
        visualization_path: Optional path to a visualization image
        
    Returns:
        PDF content as bytes
    """
    try:
        logger.info(f"Starting PDF generation for structure: {report_data.get('structure_id', 'Unknown')}")
        logger.info(f"Report data keys: {list(report_data.keys())}")
        
        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()
        
        logger.info("Creating PDF canvas")
        # Create the PDF canvas
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.darkblue)
        c.drawString(72, height - 50, "Molecular Docking Analysis Report")
        
        # Structure ID
        structure_id = report_data.get("structure_id", "Unknown")
        logger.info(f"Adding structure ID: {structure_id}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, height - 80, f"Structure ID: {structure_id}")

        # Draw a separator line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(72, height - 90, width - 72, height - 90)

        # Set starting position for content
        y_position = height - 120
        
        # Check if we have structured sections or should use raw report
        has_structured_sections = any([
            report_data.get("summary", "").strip(),
            report_data.get("binding_analysis", "").strip(),
            report_data.get("efficacy_evaluation", "").strip(),
            report_data.get("recommendations", "").strip()
        ])
        
        logger.info(f"Has structured sections: {has_structured_sections}")
        
        if has_structured_sections:
            logger.info("Processing structured sections")
            # Add each section that has content
            sections = [
                ("Executive Summary", report_data.get("summary", "")),
                ("Binding Analysis", report_data.get("binding_analysis", "")),
                ("Efficacy Evaluation", report_data.get("efficacy_evaluation", "")),
                ("Comparative Analysis", report_data.get("comparison", "")),
                ("Recommendations", report_data.get("recommendations", ""))
            ]
            
            for section_title, section_content in sections:
                if section_content.strip():
                    logger.info(f"Adding section: {section_title}")
                    # Add section header
                    c.setFont("Helvetica-Bold", 14)
                    c.setFillColor(colors.darkblue)
                    c.drawString(72, y_position, section_title)
                    y_position -= 25
                    
                    # Add section content
                    c.setFont("Helvetica", 11)
                    c.setFillColor(colors.black)
                    
                    # Process content to remove markdown styling
                    clean_content = section_content.replace("*", "")
                    
                    lines = simpleSplit(clean_content, "Helvetica", 11, width - 144)
                    for line in lines:
                        if y_position < 72:  # If near bottom of page, start a new page
                            c.showPage()
                            y_position = height - 50
                        
                        c.drawString(72, y_position, line)
                        y_position -= 15
                    
                    y_position -= 20  # Extra space between sections
        else:
            logger.info("Using raw report")
            # Use the raw report if structured sections are empty
            c.setFont("Helvetica", 11)
            c.setFillColor(colors.black)
            
            raw_report = report_data.get("raw_report", "No data available")
            logger.info(f"Raw report length: {len(raw_report)}")
            
            # Remove markdown formatting for better display
            clean_report = raw_report.replace("##", "").replace("**", "")
            
            # Split by lines first to handle section headers better
            paragraphs = clean_report.split("\n\n")
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    if ":" in paragraph and len(paragraph) < 80:
                        # This might be a header
                        c.setFont("Helvetica-Bold", 12)
                        c.setFillColor(colors.darkblue)
                        
                        lines = simpleSplit(paragraph, "Helvetica-Bold", 12, width - 144)
                        for line in lines:
                            if y_position < 72:
                                c.showPage()
                                y_position = height - 50
                            
                            c.drawString(72, y_position, line)
                            y_position -= 15
                        
                        y_position -= 10
                        c.setFont("Helvetica", 11)
                        c.setFillColor(colors.black)
                    else:
                        lines = simpleSplit(paragraph, "Helvetica", 11, width - 144)
                        for line in lines:
                            if y_position < 72:
                                c.showPage()
                                y_position = height - 50
                            
                            c.drawString(72, y_position, line)
                            y_position -= 15
                    
                    y_position -= 10  # Extra space between paragraphs
        
        # Add data visualization for scores if available
        if report_data.get("docking_scores") or report_data.get("binding_energies"):
            logger.info("Would add data visualization here (scores available)")
            # This would be implemented with charts if needed
            pass
        
        # Add metadata footer
        logger.info("Adding metadata footer")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(72, 40, f"Report generated: {report_data.get('timestamp', 'Unknown date')}")
        c.drawString(72, 25, f"Ligands: {report_data.get('ligand_count', 0)}, Chains: {report_data.get('chain_count', 0)}")
        
        # Finalize the PDF
        logger.info("Saving PDF")
        c.save()
        
        # Get the PDF content and reset the buffer position
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Error in PDF generation: {str(e)}")
        logger.error(traceback.format_exc())
        # Return error information as bytes to prevent the endpoint from failing
        error_buffer = io.BytesIO()
        c = canvas.Canvas(error_buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, 500, "Error generating PDF report")
        c.setFont("Helvetica", 12)
        c.drawString(72, 480, f"Error: {str(e)}")
        c.save()
        error_buffer.seek(0)
        return error_buffer.getvalue()