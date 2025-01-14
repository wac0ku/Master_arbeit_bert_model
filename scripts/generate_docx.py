from docx import Document
from docx.shared import Pt
import os
from logging_progress import setup_logger

logger = setup_logger("generate_docx")

def create_docx(summary, recommendations, output_path):
    """Create a DOCX file with a summary and recommendations."""
    try:
        # Ensure the results directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = Document()
        doc.add_heading('Summary', level=1)
        doc.add_paragraph(summary)

        doc.add_heading('Recommendations', level=1)
        for rec in recommendations:
            doc.add_paragraph(rec, style='List Bullet')

        doc.save(output_path)
        logger.info(f"DOCX file saved successfully: {output_path}")
    except Exception as e:
        logger.error(f"Error creating DOCX file: {e}")

if __name__ == "__main__":
    summary = "This is a sample summary of the text."
    recommendations = [
        "Recommendation 1: Implement feature X.",
        "Recommendation 2: Improve process Y.",
        "Recommendation 3: Optimize resource Z."
    ]
    output_path = "results/report.docx"
    create_docx(summary, recommendations, output_path)
