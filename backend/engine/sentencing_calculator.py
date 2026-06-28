def calculate_sentencing_range(counts: list[dict], jurisdiction: str) -> dict:
    """
    Calculates the combined sentencing range for a defendant with multiple conviction counts.
    
    Args:
        counts: [{"crime": str, "min_years": float, "max_years": float}, ...]
        jurisdiction: str (e.g. 'California', 'Federal', 'New York')
    
    Returns:
        dict containing cumulative bounds and concurrent/consecutive analysis
    """
    if not counts:
        return {
            "cumulative_min": 0.0,
            "cumulative_max": 0.0,
            "typical_concurrent": 0.0,
            "typical_consecutive": 0.0,
            "jurisdiction_practice": "No counts provided",
            "notes": ""
        }

    # Cumulative calculations
    cumulative_min = sum(count.get("min_years", 0) for count in counts)
    cumulative_max = sum(count.get("max_years", 0) for count in counts)
    
    # Highest single count (typical concurrent sentence anchor)
    highest_min = max(count.get("min_years", 0) for count in counts)
    highest_max = max(count.get("max_years", 0) for count in counts)

    # Determine jurisdiction practice
    practice = "Judicial Discretion"
    notes = ""
    jurisdiction_lower = jurisdiction.lower()
    
    if "california" in jurisdiction_lower:
        # California typically stacks one principal term (100%) and subordinate terms (1/3 of middle term)
        practice = "Principal/Subordinate Term Stacking (determinate sentencing)"
        notes = "California Penal Code Section 1170.1 typically applies: full base term for principal offense, 1/3 of middle term for subordinate consecutive offenses."
    elif "federal" in jurisdiction_lower:
        # Federal uses complex grouping
        practice = "Federal Sentencing Guidelines Grouping"
        notes = "U.S. Sentencing Guidelines (USSG) §3D1.1-3D1.5 group closely related counts. The total punishment cannot exceed the statutory maximum of all counts stacked."
    elif "new york" in jurisdiction_lower:
        practice = "Concurrent presumption unless statutorily required otherwise"
        notes = "Under NY Penal Law 70.25, sentences for offenses committed through a single act must run concurrently."
    
    return {
        "cumulative_min": cumulative_min,
        "cumulative_max": cumulative_max,
        "typical_concurrent": highest_max,  # Usually the max of the highest charge
        "typical_consecutive": cumulative_max, # Usually the sum of all charges
        "jurisdiction_practice": practice,
        "notes": notes
    }
