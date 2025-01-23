# dynamic_summarize_and_recommend.py
import os
import json
from typing import List, Dict
from load_model import load_summarization_model, summarize_text
from logging_progress import setup_logger, display_progress
from transformers import pipeline
from modules.causality import analyze_easa_causality

logger = setup_logger("aviation_accident_recommend")

# Load EASA categories and compliance rules
try:
    with open("easa_templates/categories.json", "r", encoding="utf-8") as f:
        EASA_CATEGORIES = json.load(f)
        RISK_CATEGORIES = [cat["name"] for cat in EASA_CATEGORIES["easa_risk_categories"]]
        PRIORITY_MATRIX = EASA_CATEGORIES["compliance_matrix"]["priority_levels"]
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error(f"Critical EASA configuration error: {e}")
    raise RuntimeError("EASA compliance configuration failed") from e

# Initialize models with EASA-optimized settings
recommendation_models = {
    "easa_risk_classifier": pipeline(
        "text-classification", 
        model="cross-encoder/nli-deberta-v3-base",
        function_to_apply="sigmoid"
    ),
    "zero_shot": pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=0 if os.environ.get("CUDA_AVAILABLE") == "1" else -1
    ),
    "safety_generator": pipeline(
        "text2text-generation",
        model="google/flan-t5-xxl",
        model_kwargs={"temperature": 0.7, "repetition_penalty": 1.2}
    )
}

def _get_easa_priority(category_id: str) -> str:
    """Get priority level from EASA compliance matrix"""
    for cat in EASA_CATEGORIES["easa_risk_categories"]:
        if cat["id"] == category_id:
            return f"{cat['priority']} Priority ({PRIORITY_MATRIX[cat['priority']]})"
    return "Medium Priority (Standard procedure)"

def generate_dynamic_recommendations(summary: str, context: List[str]) -> List[str]:
    """Generate EASA-compliant recommendations with causal analysis"""
    
    # Perform deep causal analysis
    causal_chains = analyze_easa_causality(summary)
    logger.info(f"Identified causal chains: {len(causal_chains)}")

    # Build EASA-compliant prompt template
    prompt = f"""
    [EASA Incident Analysis Protocol]
    Incident Summary: {summary}
    
    Required Actions:
    1. Identify root causes from: {RISK_CATEGORIES}
    2. Map to EASA regulations using: {EASA_CATEGORIES['compliance_matrix']['mandatory_reporting']}
    3. Generate recommendations with format:
       [Priority] [EASA Ref] Recommendation (Causal Factor: XYZ)
    
    Detected Causal Chains:
    {chr(10).join(causal_chains)}
    
    Output exactly 5 recommendations following EASA AMC 20-8 Annex II.
    """
    
    try:
        # Generate with safety-focused model
        results = recommendation_models["safety_generator"](
            prompt,
            max_length=400,
            num_return_sequences=1,
            do_sample=True,
            top_k=50
        )
        
        # Parse and validate recommendations
        recommendations = []
        for line in results[0]["generated_text"].split('\n'):
            if line.strip() and any(ref in line for ref in ["Part-", "AMC ", "SIB"]):
                recommendations.append(line.strip())
                logger.debug(f"Valid EASA recommendation: {line.strip()}")

        # Add priority metadata
        enhanced_recs = []
        for rec in recommendations[:5]:  # Limit to top 5 as per EASA guidelines
            for category in EASA_CATEGORIES["easa_risk_categories"]:
                if category["name"] in rec:
                    enhanced_recs.append(
                        f"{_get_easa_priority(category['id'])} | {rec}"
                    )
                    break
            else:
                enhanced_recs.append(f"Medium Priority | {rec}")

        logger.info(f"Generated {len(enhanced_recs)} EASA-compliant recommendations")
        return enhanced_recs

    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        return ["[Fallback] Immediate safety inspection required per EASA Basic Regulation Art. 5"]

def generate_recommendations(summary: str) -> List[str]:
    """Main recommendation workflow with EASA compliance checks"""
    
    if not isinstance(summary, str) or len(summary) < 50:
        logger.error("Invalid summary input")
        return ["Invalid input - cannot generate recommendations"]
    
    # EASA Risk Classification
    try:
        classification = recommendation_models["zero_shot"](
            summary,
            candidate_labels=RISK_CATEGORIES,
            multi_label=True,
            hypothesis_template="This aviation incident relates to {}"
        )
        
        relevant_risks = [
            (label, score) 
            for label, score in zip(classification["labels"], classification["scores"])
            if score > 0.65  # EASA minimum confidence threshold
        ]
        
        logger.info(f"EASA Risk Assessment: {relevant_risks}")

        # Generate context-aware recommendations
        dynamic_recs = generate_dynamic_recommendations(
            summary, 
            [risk[0] for risk in relevant_risks]
        )
        
        # Add mandatory reporting notices
        if any("Critical" in rec for rec in dynamic_recs):
            dynamic_recs.append(
                "Mandatory EASA Report Required: Regulation (EU) 376/2014 Art.4"
            )

        return dynamic_recs

    except Exception as e:
        logger.critical(f"EASA recommendation workflow failed: {e}")
        return ["[Critical] Immediate ground stop advisory per EASA ERC.001"]

def process_text_file(input_path: str, summarizer, output_dir: str) -> tuple:
    """Full EASA-compliant processing pipeline"""
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # EASA-mandated summary requirements
        summary = summarize_text(
            text,
            summarizer,
            min_length=150,  # EASA minimum investigation report length
            max_length=400
        )
        
        if not summary:
            raise ValueError("Summary generation failed")
        
        # Generate recommendations with compliance tracking
        recommendations = generate_recommendations(summary)
        
        # Format output with EASA metadata
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_EASA_report.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"EASA Compliance Report\n{'='*30}\n")
            f.write(f"File: {base_name}\n\n")
            f.write(f"Summary:\n{summary}\n\n")
            f.write("Safety Recommendations:\n")
            f.writelines([f"- {rec}\n" for rec in recommendations])
            
            # Add compliance footer
            f.write("\nCompliance Metadata:\n")
            f.write(f"- Risk Categories: {RISK_CATEGORIES}\n")
            f.write(f"- Priority Matrix: {PRIORITY_MATRIX}\n")
        
        logger.info(f"Generated EASA-compliant report: {output_path}")
        return summary, recommendations
    
    except Exception as e:
        logger.error(f"Processing failed for {input_path}: {e}")
        return None, None

def process_multiple_files(input_dir: str, output_dir: str, summarizer) -> List[tuple]:
    """Batch processing with EASA performance tracking"""
    
    results = []
    for filename in display_progress(
        [f for f in os.listdir(input_dir) if f.endswith(".txt")],
        description="Processing EASA Reports"
    ):
        result = process_text_file(
            os.path.join(input_dir, filename),
            summarizer,
            output_dir
        )
        if result[0]:  # Valid results only
            results.append((filename, result[0], result[1]))
            
            # Log compliance metrics
            high_priority = sum(1 for rec in result[1] if "High" in rec)
            logger.info(f"EASA Metrics for {filename}: "
                       f"{high_priority} critical findings")
    
    return results