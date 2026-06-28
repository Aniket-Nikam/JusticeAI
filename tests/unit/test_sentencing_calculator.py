import pytest
from backend.engine.sentencing_calculator import calculate_sentencing_range

def test_single_count():
    counts = [{"crime": "Theft", "min_years": 1.0, "max_years": 3.0}]
    result = calculate_sentencing_range(counts, "Texas")
    
    assert result["cumulative_min"] == 1.0
    assert result["cumulative_max"] == 3.0
    assert result["typical_concurrent"] == 3.0
    assert result["typical_consecutive"] == 3.0

def test_multiple_counts():
    counts = [
        {"crime": "Count 1: Sexual Assault", "min_years": 3.0, "max_years": 8.0},
        {"crime": "Count 2: Sexual Assault", "min_years": 3.0, "max_years": 8.0},
        {"crime": "Count 3: Sexual Assault", "min_years": 3.0, "max_years": 8.0}
    ]
    result = calculate_sentencing_range(counts, "California")
    
    assert result["cumulative_min"] == 9.0
    assert result["cumulative_max"] == 24.0
    assert result["typical_concurrent"] == 8.0
    assert result["typical_consecutive"] == 24.0
    assert "California Penal Code" in result["notes"]

def test_empty_counts():
    result = calculate_sentencing_range([], "Federal")
    assert result["cumulative_min"] == 0.0
    assert result["cumulative_max"] == 0.0
