import os
from logging_progress import setup_logger, display_progress
from pdf_to_txt import convert_all_pdfs
from preprocess_text import preprocess_txt
from summarize_and_recommend import process_multiple_files
from load_model import load_summarization_model
from generate_docx import create_docx

logger = setup_logger("main")

def main():
    """Main workflow to process PDF files and generate summaries and recommendations."""
    try:
        # Step 1: Convert PDF files to TXT format
        logger.info("Converting PDF files to TXT format...")
        pdf_input_dir = "data/raw_pdf"
        raw_txt_output_dir = "data/raw_txt"
        
        if not os.listdir(raw_txt_output_dir):  # Check if the directory is empty
            convert_all_pdfs(pdf_input_dir, raw_txt_output_dir)
        else:
            logger.info("TXT files already exist, skipping conversion.")

        # Step 2: Preprocess the TXT files
        logger.info("Preprocessing TXT files...")
        cleaned_txt_output_dir = "data/cleaned_data"
        
        if not os.listdir(cleaned_txt_output_dir):  # Check if the directory is empty
            preprocess_txt(raw_txt_output_dir, cleaned_txt_output_dir)
        else:
            logger.info("Cleaned files already exist, skipping preprocessing.")

        # Step 3: Load the summarization model
        logger.info("Loading summarization model...")
        summarizer = load_summarization_model()
        
        # Step 4: Generate summaries and recommendations
        logger.info("Generating summaries and recommendations...")
        results_txt_dir = "results/txt"
        results_docx_dir = "results/docx"
        os.makedirs(results_txt_dir, exist_ok=True)  # Ensure results TXT directory exists
        os.makedirs(results_docx_dir, exist_ok=True)  # Ensure results DOCX directory exists

        
        # Check if all results already exist
        all_results_exist = True
        for txt_file in os.listdir(cleaned_txt_output_dir):
            if txt_file.endswith('.txt'):
                result_txt_path = os.path.join(results_txt_dir, f"{os.path.splitext(txt_file)[0]}_results.txt")
                result_docx_path = os.path.join(results_docx_dir, f"{os.path.splitext(txt_file)[0]}_report.docx")
                if not (os.path.exists(result_txt_path) and os.path.exists(result_docx_path)):

                    all_results_exist = False
                    break
        
        if all_results_exist:
            logger.info("All results already exist, skipping the entire workflow.")
            return
        
        results = process_multiple_files(cleaned_txt_output_dir, results_txt_dir, summarizer)
        
        if results:
            # Step 5: Save results in DOCX format
            for file_name, summary, recommendations in results:
                docx_output_path = os.path.join(results_docx_dir, f"{file_name}_report.docx")

                create_docx(summary, recommendations, docx_output_path)
                logger.info(f"Results saved to {docx_output_path}")
        else:
            logger.error("No results generated.")
        
        logger.info("Workflow completed successfully")
    except Exception as e:
        logger.error(f"Error in main workflow: {e}")

if __name__ == "__main__":
    main()
