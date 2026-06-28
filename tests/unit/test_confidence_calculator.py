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
    assert result["breakdown"]["legal_compliance"] == 100
    assert result["breakdown"]["precedent_match"] == 100
    assert result["breakdown"]["absence_of_bias"] == 100

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
    assert result["score"] == 91
    assert result["breakdown"]["legal_compliance"] == 75

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
    
    assert result["score"] == 48
    assert result["breakdown"]["legal_compliance"] == 40
    assert result["breakdown"]["precedent_match"] == 50
    assert result["breakdown"]["absence_of_bias"] == 55
