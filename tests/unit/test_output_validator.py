import pytest
from backend.engine.output_validator import OutputValidator

def test_valid_output():
    validator = OutputValidator()
    raw_json = """
    {
      "layer1_result": {},
      "layer2_result": {},
      "layer3_result": {},
      "layer4_result": {},
      "layer5_result": {},
      "verdict_classification": "CONSISTENT",
      "recommended_range_min_months": 12,
      "recommended_range_max_months": 24,
      "full_reasoning_chain": "Reasoning...",
      "summary": "Summary",
      "citations": []
    }
    """
    parsed = validator.parse_and_validate(raw_json)
    assert parsed["verdict_classification"] == "CONSISTENT"

def test_missing_keys_raises_error():
    validator = OutputValidator()
    raw_json = '{"layer1_result": {}}'
    with pytest.raises(ValueError):
        validator.parse_and_validate(raw_json)

def test_invalid_verdict_defaults_to_anomalous():
    validator = OutputValidator()
    raw_json = """
    {
      "layer1_result": {}, "layer2_result": {}, "layer3_result": {}, 
      "layer4_result": {}, "layer5_result": {}, 
      "verdict_classification": "MADE_UP_WORD",
      "recommended_range_min_months": 12, "recommended_range_max_months": 24,
      "full_reasoning_chain": "", "summary": "", "citations": []
    }
    """
    parsed = validator.parse_and_validate(raw_json)
    assert parsed["verdict_classification"] == "ANOMALOUS"
