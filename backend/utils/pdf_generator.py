import io
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_docking_table(data: List[Dict[str, Any]]) -> List:
    """Create a formatted table for docking results"""
    table_data = [["Mode", "Binding Affinity (kcal/mol)", "RMSD Lower", "RMSD Upper"]]

    for entry in data:
        table_data.append(
            [
                str(entry.get("mode", "")),
                str(entry.get("affinity", "")),
                str(entry.get("rmsd_lb", "")),
                str(entry.get("rmsd_ub", "")),
            ]
        )

    return table_data


async def create_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """
    Create a PDF report from the structured data returned by the LLM.

    Args:
        report_data: Dictionary containing the structured report data

    Returns:
        PDF content as bytes
    """
    try:
        logger.info(
            f"Starting PDF generation for structure: {report_data.get('structure_id', 'Unknown')}"
        )
        logger.info(f"Report data keys: {list(report_data.keys())}")

        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()

        # Use SimpleDocTemplate for more complex layouts
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Container for the elements to be added to the document
        elements = []

        # Styles for text
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        heading_style = styles["Heading1"]
        subheading_style = styles["Heading2"]
        normal_style = styles["Normal"]

        # Title
        elements.append(Paragraph("Molecular Docking Analysis Report", title_style))

        # Structure ID if available
        structure_id = report_data.get("structure_id", "Unknown")
        elements.append(Paragraph(f"Structure ID: {structure_id}", subheading_style))

        # Best binding mode info
        best_mode = report_data.get("best_binding_mode")
        best_affinity = report_data.get("best_affinity")
        if best_mode and best_affinity:
            elements.append(
                Paragraph(
                    f"Best Binding Mode: {best_mode} (Affinity: {best_affinity} kcal/mol)",
                    subheading_style,
                )
            )

        # Date and timestamp
        timestamp = report_data.get("timestamp", datetime.now().isoformat())
        elements.append(Paragraph(f"Report generated: {timestamp}", normal_style))
        elements.append(Paragraph(" ", normal_style))  # Add some space

        # Add docking results table if available
        docking_results = report_data.get("docking_results", [])
        if docking_results:
            elements.append(Paragraph("Docking Results Summary", heading_style))

            # Create table
            table_data = create_docking_table(docking_results)
            t = Table(table_data)

            # Style the table
            table_style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.darkblue),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )

            # Highlight the best binding mode
            if best_mode and 1 <= best_mode <= len(docking_results):
                table_style.add(
                    "BACKGROUND", (0, best_mode), (-1, best_mode), colors.lightgreen
                )

            t.setStyle(table_style)
            elements.append(t)
            elements.append(Paragraph(" ", normal_style))  # Add some space

        # Process the raw report or structured sections for the main content
        raw_report = report_data.get("raw_report", "")
        if raw_report:
            # Split by markdown headers and process
            sections = raw_report.split("**")

            for i, section in enumerate(sections):
                section = section.strip()
                if not section:
                    continue

                if (
                    i % 2 == 1
                ):  # This is a header (odd sections are headers in the pattern)
                    # Clean up the section header
                    clean_header = section.replace(":", "").strip()
                    elements.append(Paragraph(clean_header, heading_style))
                else:
                    # This is content
                    # Split paragraphs and process
                    paragraphs = section.split("\n\n")
                    for para in paragraphs:
                        if para.strip():
                            # Check if it's a table (markdown table)
                            if "|---" in para:
                                # Handle tables later if needed
                                pass
                            else:
                                elements.append(Paragraph(para.strip(), normal_style))

        # Build the document with all elements
        doc.build(elements)

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
