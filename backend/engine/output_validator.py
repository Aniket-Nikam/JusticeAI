import json
import logging

logger = logging.getLogger(__name__)

class OutputValidator:
    def parse_and_validate(self, raw_output: str) -> dict:
        """
        Parses JSON from raw LLM output and validates structure.
        """
        try:
            # Simple cleanup in case LLM wraps output in markdown code blocks
            clean_output = raw_output.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_output)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON: {e}")
            raise ValueError("LLM returned malformed JSON.")

        required_keys = [
            "layer1_result", "layer2_result", "layer3_result", 
            "layer4_result", "layer5_result", "verdict_classification", 
            "recommended_range_min_months", "recommended_range_max_months",
            "full_reasoning_chain", "summary", "citations"
        ]

        for key in required_keys:
            if key not in parsed:
                raise ValueError(f"Missing required key in LLM output: {key}")

        valid_verdicts = [
            "CONSISTENT", "LENIENT", "SIGNIFICANTLY LENIENT", 
            "HARSH", "SIGNIFICANTLY HARSH", "ANOMALOUS"
        ]
        
        if parsed.get("verdict_classification") not in valid_verdicts:
            logger.warning(f"Invalid verdict classification {parsed.get('verdict_classification')}, defaulting to ANOMALOUS.")
            parsed["verdict_classification"] = "ANOMALOUS"

        # Ensure AI didn't hallucinate a confidence score. We calculate it.
        if "confidence_score" in parsed:
            del parsed["confidence_score"]
            
        return parsed
