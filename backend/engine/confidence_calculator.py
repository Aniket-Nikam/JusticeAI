def calculate_confidence(analysis: dict) -> dict:
    """
    Programmatically calculates the confidence score of an AI analysis based on the presence
    and quality of citations and structural requirements.
    
    Args:
        analysis: A dictionary representing the structured output from the LLM, including 'citations' list.
        
    Returns:
        dict: {"score": int, "breakdown": dict}
    """
    legal_compliance = 100
    precedent_match = 100
    absence_of_bias = 100
    
    citations = analysis.get("citations", [])
    layer_results = {
        1: analysis.get("layer1_result", {}),
        2: analysis.get("layer2_result", {}),
        3: analysis.get("layer3_result", {}),
        4: analysis.get("layer4_result", {}),
        5: analysis.get("layer5_result", {}),
    }

    # Helper functions to check citations
    def has_citation_type(layer: int, source_type_substring: str):
        return any(c.get("layer") == layer and source_type_substring.lower() in c.get("source_type", "").lower() for c in citations)

    # 1. Legal Compliance Checks
    if not has_citation_type(1, "statute") and not has_citation_type(1, "code"):
        legal_compliance -= 25

    if not has_citation_type(2, "sentencing") and not has_citation_type(2, "commission"):
        legal_compliance -= 20
        
    # 2. Precedent Match Checks
    jurisdictions_compared = layer_results[4].get("jurisdictions_compared", [])
    if len(jurisdictions_compared) < 5:
        precedent_match -= 25
        
    non_media_sources = [c for c in citations if "news" not in c.get("source_type", "").lower() and "media" not in c.get("source_type", "").lower()]
    if not non_media_sources and citations:
        precedent_match -= 25
        legal_compliance -= 15
        
    # 3. Absence of Bias Checks
    if not has_citation_type(5, "behavioral") and not has_citation_type(5, "psych"):
        absence_of_bias -= 20
        
    profile_data = layer_results[5].get("defendant_profile_assessed", False)
    if not profile_data:
        absence_of_bias -= 25
        
    # Compile breakdown
    breakdown = {
        "legal_compliance": max(20, legal_compliance),
        "precedent_match": max(20, precedent_match),
        "absence_of_bias": max(20, absence_of_bias)
    }
    
    # Calculate overall score as average
    base_score = int((breakdown["legal_compliance"] + breakdown["precedent_match"] + breakdown["absence_of_bias"]) / 3)

    return {
        "score": base_score,
        "breakdown": breakdown
    }
