from transformers import pipeline, BartTokenizer
from logging_progress import setup_logger
import os

logger = setup_logger("load_model")

# Create the models directory if it does not exist
model_directory = "models"  # Directory to store the downloaded model
os.makedirs(model_directory, exist_ok=True)

# Variable to cache the loaded model
cached_model = None

def load_summarization_model(model_name="facebook/bart-large-cnn"):
    """Load a pretrained Hugging Face model for text summarization."""
    global cached_model
    if cached_model is not None:
        logger.info("Loading model from cache...")
        return cached_model
    
    # Check if the model is already downloaded
    model_path = os.path.join(model_directory, model_name.replace("/", "_"))
    if os.path.exists(model_path):
        logger.info(f"Loading model from local directory: {model_path}")
        cached_model = pipeline("summarization", model=model_path)
        logger.info("Model loaded successfully from local directory")
        return cached_model
    
    try:
        logger.info(f"Downloading model: {model_name}")
        cached_model = pipeline("summarization", model=model_name)
        cached_model.save_pretrained(model_path)  # Save the model locally
        logger.info("Model downloaded and saved successfully")
        return cached_model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def summarize_text(text, summarizer, max_length=130, min_length=30):
    """Summarize the given text using the loaded model."""
    try:
        if not text.strip():
            logger.error("Input text is empty, cannot summarize.")
            return None
        
        if len(text) < 50:  # Check for minimum length
            logger.error("Input text is too short for summarization.")
            return None
        
        logger.info("Summarizing text")
        tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        tokenizer.pad_token = tokenizer.eos_token  # Set padding token
        
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=1024)
        
        # Generate summary with proper configuration
        summary = summarizer.model.generate(
            inputs['input_ids'],
            max_length=max_length,
            min_length=min_length,
            num_beams=4,  # Use beam search for better results
            early_stopping=True
        )
        
        if summary is None or len(summary) == 0:
            logger.error("Summary returned is empty.")
            return None
        
        logger.info("Text summarized successfully")
        return tokenizer.decode(summary[0], skip_special_tokens=True)
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return None
