import pytest
from backend.engine.confidence_calculator import calculate_confidence

def test_perfect_score():
    analysis = {
        "citations": [
            {"layer": 1, "source_type": "Official Statute Code"},
            {"layer": 2, "source_type": "Sentencing Commission Report"},
            {"layer": 5, "source_type": "Behavioral Psychology Journal"}
        ],
        "layer4_result": {
            "jurisdictions_compared": ["UK", "Canada", "Australia", "Germany", "Sweden"]
        },
        "layer5_result": {
            "defendant_profile_assessed": True
        }
    }
    result = calculate_confidence(analysis)
    assert result["score"] == 100
    assert "perfect_score" in result["breakdown"]

def test_missing_statute():
    analysis = {
        "citations": [
            {"layer": 2, "source_type": "Sentencing Commission Report"},
            {"layer": 5, "source_type": "Behavioral Psychology Journal"}
        ],
        "layer4_result": {
            "jurisdictions_compared": ["UK", "Canada", "Australia", "Germany", "Sweden"]
        },
        "layer5_result": {
            "defendant_profile_assessed": True
        }
    }
    result = calculate_confidence(analysis)
    assert result["score"] == 80
    assert result["breakdown"]["missing_statute_citation"] == -20

def test_media_only_sources():
    analysis = {
        "citations": [
            {"layer": 1, "source_type": "News Media Report"},
            {"layer": 2, "source_type": "News Article"},
        ],
        "layer4_result": {
            "jurisdictions_compared": ["UK"]
        },
        "layer5_result": {
            "defendant_profile_assessed": False
        }
    }
    result = calculate_confidence(analysis)
    
    # Base: 100
    # Missing statute (News media report doesn't match 'statute' or 'code'): -20
    # Missing sentencing: -15
    # Fewer than 5 juris: -15
    # No behavioral: -10
    # Missing profile: -10
    # Media only: -15
    # Total deductions: -85 -> Score 15, but floored at 20.
    
    assert result["score"] == 20
    assert result["breakdown"]["media_only_sources"] == -15
    assert result["breakdown"]["missing_statute_citation"] == -20
