import os
from datetime import datetime
from logging_progress import setup_logger, display_progress
from pdf_to_txt import convert_all_pdfs
from preprocess_text import preprocess_txt
from dynamic_summarize_and_recommend import process_multiple_files, recommendation_models
from load_model import load_summarization_model, clear_cached_model
from generate_docx_from_txt import generate_docx_from_txt

logger = setup_logger("main")

def main():
    """Main workflow to process PDF files and generate summaries and recommendations."""
    try:
        logger.info("Starting the main workflow.")
        
        # Step 1: Convert PDF files to TXT format
        logger.info("Converting PDF files to TXT format...")
        pdf_input_dir = "data/raw_pdf"
        raw_txt_output_dir = "data/raw_txt"
        
        # Ensure output directory exists
        os.makedirs(raw_txt_output_dir, exist_ok=True)

        # Process all PDF files
        convert_all_pdfs(pdf_input_dir, raw_txt_output_dir)

        # Step 2: Preprocess the TXT files
        logger.info("Preprocessing TXT files...")
        cleaned_txt_output_dir = "data/cleaned_data"
        os.makedirs(cleaned_txt_output_dir, exist_ok=True)  # Ensure cleaned data directory exists
        
        preprocess_txt(raw_txt_output_dir, cleaned_txt_output_dir)

        # Step 3: Load the summarization model
        logger.info("Loading summarization model...")
        summarizer = load_summarization_model()
        
        # Step 4: Generate summaries and recommendations
        logger.info("Generating summaries and recommendations...")
        today_date = datetime.now().strftime("%Y-%m-%d")
        results_txt_dir = os.path.join("results", today_date, "txt")
        os.makedirs(results_txt_dir, exist_ok=True)  # Ensure results TXT directory exists

        results = process_multiple_files(cleaned_txt_output_dir, results_txt_dir, summarizer)
        
        if results:
            # Step 5: Save results in TXT format
            for file_name, summary, recommendations in results:
                base_filename = os.path.splitext(file_name)[0]
                
                # Save the TXT file with dynamic recommendations
                txt_output_path = os.path.join(results_txt_dir, f"{base_filename}_results.txt")
                with open(txt_output_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(f"Summary:\n{summary}\n\nRecommendations:\n")
                    if isinstance(recommendations, list):
                        for rec in recommendations:
                            txt_file.write(f"- {rec}\n")
                
                logger.info(f"Results saved to {txt_output_path}")

            # Generate DOCX files from the TXT files
            results_docx_dir = os.path.join("results", today_date, "docx")
            generate_docx_from_txt(results_txt_dir, results_docx_dir)
        else:
            logger.error("No results generated.")
        
        logger.info("Workflow completed successfully")
        
        # Clear cached model to release resources
        clear_cached_model()
    except Exception as e:
        logger.error(f"Error in main workflow: {e}")

if __name__ == "__main__":
    main()
