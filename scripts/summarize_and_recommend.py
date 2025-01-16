import os
from load_model import load_summarization_model, summarize_text
from logging_progress import setup_logger, display_progress
from transformers import pipeline  # Importing BERT pipeline

logger = setup_logger("summarize_and_recommend")
logger.info("Starting recommendation generation process.")


# Load BERT model for recommendations
recommendation_model = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english") # BERT model for text classification (recommendations) 
                                                                                                                # Hierbei kann man mehrere Modelle ausprobieren, um das beste zu finden
                                                                                                                # RUSLANA, HIER ANFANGEN RUMZUSPIELEN
                                                                                                                # Ändere NUR model="distilbert-base-uncased-finetuned-sst-2-english" zu einem anderen Modell, um zu sehen, ob es besser ist
def generate_recommendations(summary):
    logger.info("Generating recommendations based on the summary.")

    """Generate recommendations based on keywords in the summary and BERT model."""
    recommendations = []
    
    if isinstance(summary, str):  # Ensure summary is a string

        # BERT-based recommendations
        bert_recommendations = recommendation_model(summary)
        logger.info(f"BERT recommendations: {bert_recommendations}")  # Log the recommendations from BERT model
        for rec in bert_recommendations:
            
            if rec['label'] == 'LABEL_1' and rec['score'] > 0.5:  # Filter out irrelevant labels and low confidence scores
                recommendations.append(rec['label'])  # Assuming the model returns labels as recommendations
    else:
        logger.error("Summary is not a valid string, cannot generate recommendations.")
    
    if not recommendations:
        recommendations.append("No specific recommendations based on the summary.")
    
    return recommendations

def process_text_file(input_path, summarizer, output_dir):
    """Process a text file to generate a summary and recommendations."""
    try:
        # Check if the results already exist
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_results.txt")
        if os.path.exists(output_path):
            logger.info(f"Overwriting existing results for {input_path}: {output_path}")
        
        with open(input_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        logger.info("Generating summary...")
        summary = summarize_text(text, summarizer)
        
        if summary is None:
            logger.error(f"Failed to generate summary for {input_path}")
            return None, None
        
        logger.info("Generating recommendations...")
        recommendations = generate_recommendations(summary)
        
        # Save results to a file
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(f"Summary:\n{summary}\n\nRecommendations:\n")
            for rec in recommendations:
                file.write(f"- {rec}\n")
        
        logger.info(f"Results saved to {output_path}")
        return summary, recommendations
    except Exception as e:
        logger.error(f"Error processing text file: {e}")
        return None, None

def process_multiple_files(input_dir, output_dir, summarizer):
    """Process multiple text files in a directory."""
    try:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
        results = []
        
        for txt_file in display_progress(txt_files, description="Processing files"):
            input_path = os.path.join(input_dir, txt_file)
            summary, recommendations = process_text_file(input_path, summarizer, output_dir)
            if summary and recommendations:
                results.append((txt_file, summary, recommendations))
        
        return results
    except Exception as e:
        logger.error(f"Error processing multiple files: {e}")
        return None
