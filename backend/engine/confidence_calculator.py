def calculate_confidence(analysis: dict) -> dict:
    """
    Programmatically calculates the confidence score of an AI analysis based on the presence
    and quality of citations and structural requirements.
    
    Args:
        analysis: A dictionary representing the structured output from the LLM, including 'citations' list.
        
    Returns:
        dict: {"score": int, "breakdown": dict}
    """
    base_score = 100
    breakdown = {}
    
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

    # 1. Missing Statute Citation (Layer 1)
    if not has_citation_type(1, "statute") and not has_citation_type(1, "code"):
        breakdown["missing_statute_citation"] = -20
        base_score -= 20

    # 2. Missing Sentencing Data Citation (Layer 2)
    if not has_citation_type(2, "sentencing") and not has_citation_type(2, "commission"):
        breakdown["missing_sentencing_data_citation"] = -15
        base_score -= 15
        
    # 3. Fewer than 5 jurisdictions compared (Layer 4)
    jurisdictions_compared = layer_results[4].get("jurisdictions_compared", [])
    if len(jurisdictions_compared) < 5:
        breakdown["fewer_than_5_jurisdictions_compared"] = -15
        base_score -= 15
        
    # 4. No behavioral science citation (Layer 5)
    if not has_citation_type(5, "behavioral") and not has_citation_type(5, "psych"):
        breakdown["no_behavioral_science_citation"] = -10
        base_score -= 10
        
    # 5. Missing defendant profile data
    profile_data = layer_results[5].get("defendant_profile_assessed", False)
    if not profile_data:
        breakdown["missing_defendant_profile_data"] = -10
        base_score -= 10
        
    # 6. Media only sources
    non_media_sources = [c for c in citations if "news" not in c.get("source_type", "").lower() and "media" not in c.get("source_type", "").lower()]
    if not non_media_sources and citations:
        breakdown["media_only_sources"] = -15
        base_score -= 15
        
    # Minimum score floor
    if base_score < 20:
        base_score = 20
        
    if not breakdown:
        breakdown["perfect_score"] = 0
        
    return {
        "score": base_score,
        "breakdown": breakdown
    }
