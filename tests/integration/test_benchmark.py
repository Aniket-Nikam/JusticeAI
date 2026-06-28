import pytest
import asyncio
from backend.engine.reasoning_pipeline import ReasoningPipeline

@pytest.mark.asyncio
async def test_brock_turner_benchmark():
    pipeline = ReasoningPipeline()
    case_data = {
        "jurisdiction": "California",
        "crime_type": "Sexual assault",
        "defendant_profile": "19-year-old male, university student, competitive swimmer, no prior record",
        "counts": [
            {"crime": "assault with intent to commit rape of an intoxicated woman", "min_years": 2, "max_years": 4},
            {"crime": "sexually penetrating an intoxicated person with a foreign object", "min_years": 3, "max_years": 8},
            {"crime": "sexually penetrating an unconscious person with a foreign object", "min_years": 3, "max_years": 8}
        ],
        "description": "Brock Turner sexually assaulted an unconscious 22-year-old woman. Found guilty by jury on all three felony counts. Sentenced to 6 months in county jail plus 3 years of probation."
    }
    
    result = await pipeline.analyze(case_data)
    
    # Assertions based on Phase 3 benchmark criteria
    assert "layer1_result" in result
    assert result["confidence_score"] > 0
    # Should identify it as lenient
    assert result["verdict_classification"] in ["LENIENT", "SIGNIFICANTLY LENIENT", "ANOMALOUS"]
    # Check that reasoning chain exists
    assert "full_reasoning_chain" in result
    assert "STEP 1" in result["full_reasoning_chain"] or "STEP 1" in str(result)
