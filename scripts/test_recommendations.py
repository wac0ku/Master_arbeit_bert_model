from load_model import load_summarization_model
from summarize_and_recommend import generate_recommendations

def test_recommendations():
    """Test the recommendations generation."""
    summarizer = load_summarization_model()
    test_summary = "The engine requires maintenance and the fuel system needs inspection for safety."
    
    recommendations = generate_recommendations(test_summary)
    
    print("Generated Recommendations:")
    for rec in recommendations:
        print(f"- {rec}")

if __name__ == "__main__":
    test_recommendations()
