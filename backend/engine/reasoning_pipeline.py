import os
import logging
from .data_sourcer import DataPreFetcher
from .prompt_builder import PromptBuilder
from .output_validator import OutputValidator
from .confidence_calculator import calculate_confidence
from .sentencing_calculator import calculate_sentencing_range
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class ReasoningPipeline:
    def __init__(self):
        self.prefetcher = DataPreFetcher()
        self.prompt_builder = PromptBuilder()
        self.output_validator = OutputValidator()
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        # We use a reliable JSON model for structured output
        self.model = "llama-3.3-70b-versatile" 

    async def analyze(self, case_dict: dict) -> dict:
        """
        Runs the full JusticeAI reasoning pipeline.
        case_dict should contain full case info like jurisdiction, crime_type, counts, etc.
        """
        logger.info(f"Starting analysis for case: {case_dict.get('crime_type')}")
        
        # 1. Calculate Sentencing (Rule-based)
        counts = case_dict.get("counts", [])
        if not counts:
            # Fallback if the legacy frontend didn't pass array of counts
            # Build a mock count from the description for backward compatibility
            counts = [{"crime": case_dict.get("crime_type", "Unknown"), "min_years": 0.0, "max_years": 10.0}]
            
        sentencing_calc = calculate_sentencing_range(counts, case_dict.get("jurisdiction", "Unknown"))
        
        # 2. Prefetch Live Data (Web scraping)
        logger.info("Prefetching live data via DuckDuckGo...")
        prefetched = await self.prefetcher.prefetch_all(case_dict)
        
        # 3. Build Prompt
        logger.info("Building Prompt...")
        prompt = self.prompt_builder.build_case_prompt(case_dict, prefetched, sentencing_calc)
        
        # 4. Execute AI
        logger.info(f"Executing LLM reasoning via {self.model}...")
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        raw_output = completion.choices[0].message.content
        
        # 5. Parse and Validate
        logger.info("Parsing and validating output...")
        parsed = self.output_validator.parse_and_validate(raw_output)
        
        # 6. Calculate Confidence
        logger.info("Calculating objective confidence score...")
        confidence = calculate_confidence(parsed)
        parsed["confidence_score"] = confidence["score"]
        parsed["confidence_breakdown"] = confidence["breakdown"]
        
        return parsed
