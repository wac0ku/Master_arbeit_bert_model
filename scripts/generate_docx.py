import os
from datetime import datetime
from docx import Document
from logging_progress import setup_logger

logger = setup_logger("generate_docx")

def create_docx(summary, recommendations, docx_dir):
    """Create a DOCX file with a summary and recommendations."""
    try:
        # Generate a timestamped filename
        today_date = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%H-%M-%S")
        base_filename = os.path.basename(docx_dir)

        docx_output_path = os.path.join(docx_dir, f"test_{today_date}_{timestamp}_{base_filename}.docx")

        # Check if the DOCX file already exists
        if os.path.exists(docx_output_path):
            logger.info(f"Overwriting existing DOCX file: {docx_output_path}")

        # Create the DOCX file
        doc = Document()
        doc.add_heading('Summary', level=1)
        doc.add_paragraph(summary)

        doc.add_heading('Recommendations', level=1)
        for rec in recommendations:
            doc.add_paragraph(rec, style='List Bullet')

        doc.save(docx_output_path)
        logger.info(f"DOCX file saved successfully: {docx_output_path}")

    except Exception as e:
        logger.error(f"Error creating DOCX file: {e}")

if __name__ == "__main__":
    summary = "This is a sample summary of the text."
    recommendations = [
        "Recommendation 1: Implement feature X.",
        "Recommendation 2: Improve process Y.",
        "Recommendation 3: Optimize resource Z."
    ]
    output_dir = "results"  # Example path, adjust as needed
    today_date = datetime.now().strftime("%Y-%m-%d")
    docx_dir = os.path.join(output_dir, today_date, "docx")  # Only handle docx_dir
    create_docx(summary, recommendations, docx_dir)
