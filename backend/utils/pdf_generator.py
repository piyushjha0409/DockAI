from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
import os

def create_pdf_report(report_text: str, visualization_path: str, output_dir: str = "reports") -> str:
   
    # Ensure the reports directory exists
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, "Docking_Report.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(100, height - 50, "Docking Analysis Report")

    # Draw a separator line
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(100, height - 60, width - 100, height - 60)

    # Report content
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)

    # Ensure long text wraps properly
    lines = simpleSplit(report_text, "Helvetica", 12, width - 200)
    y_position = height - 100  # Initial position for text

    for line in lines:
        c.drawString(100, y_position, line)
        y_position -= 20  # Move down for next line

    # Add visualization image if available
    if os.path.exists(visualization_path):
        try:
            c.drawImage(visualization_path, 100, y_position - 250, width=400, height=300)
        except Exception as e:
            print(f"Error adding image: {e}")

    c.save()
    return pdf_path
