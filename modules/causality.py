import spacy
from typing import List

nlp = spacy.load("en_core_web_sm")

def analyze_easa_causality(text: str) -> List[str]:
    """Identifiziert Ursachen gemäß EASA Risk Classification Scheme :cite[3]"""
    doc = nlp(text)
    causal_triggers = ["caused by", "due to", "root cause", "failure of"]
    return [
        sent.text for sent in doc.sents
        if any(trigger in sent.text.lower() for trigger in causal_triggers)
    ]