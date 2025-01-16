import os
import datetime
from docx import Document
from logging_progress import setup_logger

logger = setup_logger("generate_docx")

def create_docx(summary, recommendations, output_dir):
    """Create a DOCX file with a summary and recommendations."""
    try:
        # Create a directory for today's date
        today_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(output_dir, today_date)
        os.makedirs(date_dir, exist_ok=True)

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%H-%M-%S")
        output_path = os.path.join(date_dir, f"{summary[:10]}_report_{timestamp}.docx")

        # Check if the DOCX file already exists
        if os.path.exists(output_path):
            logger.info(f"Overwriting existing DOCX file: {output_path}")

        # Create the DOCX file
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
    output_dir = "results/docx"  # Example path, adjust as needed
    create_docx(summary, recommendations, output_dir)