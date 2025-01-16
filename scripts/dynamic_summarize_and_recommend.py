import os
from load_model import load_summarization_model, summarize_text
from logging_progress import setup_logger, display_progress
from transformers import pipeline

logger = setup_logger("aviation_accident_recommend")
logger.info("Starting aviation accident analysis process.")

# Initialize recommendation models
recommendation_models = {
    "distilbert": pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english"),
    "roberta": pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment"),
    "deberta": pipeline("text-classification", model="microsoft/deberta-v3-base"),
    "zero_shot": pipeline("zero-shot-classification", model="facebook/bart-large-mnli"),
    "generator": pipeline("text2text-generation", model="google/flan-t5-base")
}

def generate_dynamic_recommendations(summary, context):
    """Generate dynamic recommendations based on the summary content."""
    
    prompt = f"""
    Based on this aviation incident summary: '{summary}'
    Generate specific safety recommendations. Focus on:
    - Direct causes mentioned
    - Safety improvements
    - Preventive measures
    - Technical solutions
    Return only the recommendations, one per line.
    """
    
    try:
        # Generate recommendations with the T5 model
        generated_recommendations = recommendation_models["generator"](
            prompt, 
            max_length=200,
            num_return_sequences=1  # Change this to 1 to comply with the model's requirements
        )
        
        recommendations = []
        for gen in generated_recommendations:
            recs = gen['generated_text'].split('\n')
            recs = [r.strip() for r in recs if r.strip()]
            recommendations.extend(recs)
            
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating dynamic recommendations: {e}")
        return ["Unable to generate specific recommendations"]

def generate_recommendations(summary):
    logger.info("Generating recommendations based on the summary.")

    recommendations = []
    
    if isinstance(summary, str):
        # Existing model recommendations
        for model_name, model in recommendation_models.items():
            if model_name in ["distilbert", "roberta", "deberta"]:
                model_recommendations = model(summary)
                logger.info(f"{model_name} recommendations: {model_recommendations}")
                
                for rec in model_recommendations:
                    if rec['label'] == 'LABEL_1' and rec['score'] > 0.5:
                        recommendations.append(f"{model_name}: {rec['label']}")

        # Zero-Shot classification for context
        aviation_categories = [
            "fuel system issues",
            "mechanical failures",
            "weather conditions",
            "pilot error",
            "maintenance issues",
            "communication problems"
        ]
        
        context_results = recommendation_models["zero_shot"](
            summary,
            candidate_labels=aviation_categories,
            multi_label=True
        )
        
        relevant_categories = [
            label for label, score in zip(context_results['labels'], context_results['scores'])
            if score > 0.3
        ]
        
        # Generate dynamic recommendations based on the context
        dynamic_recs = generate_dynamic_recommendations(summary, relevant_categories)
        
        if dynamic_recs:
            recommendations.extend(dynamic_recs)
        
    else:
        logger.error("Summary is not a valid string, cannot generate recommendations.")
    
    if not recommendations:
        recommendations.append("No specific recommendations based on the summary.")
    
    return recommendations

def process_text_file(input_path, summarizer, output_dir):
    """Process a text file to generate a summary and recommendations."""
    try:
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
