import os
import re
from langdetect import detect
from logging_progress import setup_logger, display_progress

logger = setup_logger("preprocess_text")

def clean_text(text):
    """Clean the input text by removing unnecessary characters and whitespace."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    return text.strip()

def preprocess_txt(input_dir, output_dir):
    """Preprocess TXT files in the input directory and save cleaned files in the output directory."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]

        for txt_file in display_progress(txt_files, description="Cleaning text files"):
            input_path = os.path.join(input_dir, txt_file)
            output_path = os.path.join(output_dir, txt_file)

            # Check if the cleaned file already exists
            if os.path.exists(output_path):
                logger.info(f"Skipping {txt_file}, cleaned file already exists: {output_path}")
                continue

            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()

            cleaned_text = clean_text(text)
            language = detect(cleaned_text)

            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_text)

            logger.info(f"Processed {txt_file} - Detected language: {language}")

    except Exception as e:
        logger.error(f"Error processing TXT files: {e}")
