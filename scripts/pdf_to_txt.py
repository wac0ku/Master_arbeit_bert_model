import fitz  # PyMuPDF
import os
from datetime import datetime
from logging_progress import setup_logger, display_progress

logger = setup_logger("pdf_to_txt")

def pdf_to_txt(pdf_path, output_dir):
    """Convert a PDF file to a TXT file and save it in the output directory."""
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract the base name of the PDF file
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_path = os.path.join(output_dir, f"{base_name}.txt")

        # Check if the corresponding TXT file already exists
        if os.path.exists(txt_path):
            logger.info(f"Skipping extraction of text, already exists: {txt_path}")
            return

        # Open the PDF file
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in display_progress(doc, description="Extracting text"):
                text += page.get_text()

        # Write the extracted text to a TXT file
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        logger.info(f"Successfully converted {pdf_path} to {txt_path}")
        return txt_path

    except Exception as e:
        logger.error(f"Error converting {pdf_path}: {e}")
        return None

def convert_all_pdfs(input_dir, output_dir):
    """Convert all PDF files in the input directory to TXT format."""
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            pdf_to_txt(pdf_path, output_dir)
