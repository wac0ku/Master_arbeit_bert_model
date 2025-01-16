import os
from datetime import datetime
from logging_progress import setup_logger, display_progress
from pdf_to_txt import convert_all_pdfs
from preprocess_text import preprocess_txt
from dynamic_summarize_and_recommend import process_multiple_files, recommendation_models
from load_model import load_summarization_model, clear_cached_model
from generate_docx import create_docx

logger = setup_logger("main")

def main():
    """Main workflow to process PDF files and generate summaries and recommendations."""
    try:
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
        results_docx_dir = os.path.join("results", today_date, "docx")
        os.makedirs(results_txt_dir, exist_ok=True)  # Ensure results TXT directory exists
        os.makedirs(results_docx_dir, exist_ok=True)  # Ensure results DOCX directory exists

        results = process_multiple_files(cleaned_txt_output_dir, results_txt_dir, summarizer)
        
        if results:
            # Step 5: Save results in both formats
            for file_name, summary, recommendations in results:
                timestamp = datetime.now().strftime("%H-%M-%S")
                base_filename = os.path.splitext(file_name)[0]
                
                # Save results for each model
                for model_name in recommendation_models.keys():
                    txt_output_path = os.path.join(results_txt_dir, f"test_{today_date}_{timestamp}_{model_name}_{base_filename}.txt")
                    docx_output_path = os.path.join(results_docx_dir, f"test_{today_date}_{timestamp}_{model_name}_{base_filename}.docx")

                    # Save the TXT file with dynamic recommendations
                    with open(txt_output_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(f"Summary:\n{summary}\n\nRecommendations:\n")
                        if isinstance(recommendations, list):
                            for rec in recommendations:
                                if isinstance(rec, dict):
                                    # Handle structured recommendations
                                    txt_file.write(f"\nFrom {model_name}:\n")
                                    if 'category' in rec:
                                        txt_file.write(f"Category: {rec['category']}\n")
                                    if 'context' in rec:
                                        txt_file.write(f"Context: {rec['context']}\n")
                                    if 'recommendations' in rec:
                                        for subrec in rec['recommendations']:
                                            txt_file.write(f"- {subrec}\n")
                                else:
                                    # Handle simple string recommendations
                                    txt_file.write(f"- {rec}\n")
                        else:
                            txt_file.write(f"- {recommendations}\n")
                    
                    logger.info(f"Results saved to {txt_output_path}")
                    
                    # Save the DOCX file
                    create_docx(summary, recommendations, results_docx_dir)
                    logger.info(f"DOCX file saved to {docx_output_path}")
        else:
            logger.error("No results generated.")
        
        logger.info("Workflow completed successfully")
        
        # Clear cached model to release resources
        clear_cached_model()
    except Exception as e:
        logger.error(f"Error in main workflow: {e}")

if __name__ == "__main__":
    main()
