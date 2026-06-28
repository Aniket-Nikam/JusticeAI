import os
import asyncio
import logging
import json
from .data_sourcer import DataPreFetcher
from .output_validator import OutputValidator
from .confidence_calculator import calculate_confidence
from .sentencing_calculator import calculate_sentencing_range
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SwarmReasoningPipeline:
    def __init__(self):
        self.prefetcher = DataPreFetcher()
        self.output_validator = OutputValidator()
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        with open(os.path.join(self.prompts_dir, "system_prompt.md"), "r", encoding="utf-8") as f:
            self.base_system_prompt = f.read()

    async def _run_sub_agent(self, layer_id: int, prompt_text: str, user_message: str) -> dict:
        """Runs an independent sub-agent for a specific reasoning layer."""
        system_content = f"{self.base_system_prompt}\n\n{prompt_text}\n\nWARNING: You are a sub-agent ONLY responsible for Layer {layer_id}. Return ONLY the JSON for your layer and any citations you found."
        
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            raw_output = completion.choices[0].message.content
            clean_output = raw_output.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_output)
        except Exception as e:
            logger.error(f"Sub-agent {layer_id} failed: {e}")
            return {f"layer{layer_id}_result": {"status": "ERROR", "finding": str(e)}, "citations": []}

    async def analyze(self, case_dict: dict, historical_challenges: list = None) -> dict:
        """
        Runs the Multi-Agent Swarm pipeline with Agentic Memory injection.
        """
        if historical_challenges is None:
            historical_challenges = []
            
        logger.info(f"Starting Multi-Agent Swarm for case: {case_dict.get('crime_type')}")
        
        counts = case_dict.get("counts", [])
        if not counts:
            counts = [{"crime": case_dict.get("crime_type", "Unknown"), "min_years": 0.0, "max_years": 10.0}]
            
        sentencing_calc = calculate_sentencing_range(counts, case_dict.get("jurisdiction", "Unknown"))
        prefetched = await self.prefetcher.prefetch_all(case_dict)
        
        # Build memory block
        memory_block = "None"
        if historical_challenges:
            memory_block = ""
            for i, ch in enumerate(historical_challenges):
                memory_block += f"PAST MISTAKE {i+1} (Layer {ch.get('layer', 'Any')}): {ch.get('text', '')}\n"
        
        user_message = f"""
        <AGENTIC_MEMORY>
        The following are PAST MISTAKES you have made on similar cases. You are FORBIDDEN from repeating them:
        {memory_block}
        </AGENTIC_MEMORY>

        CASE DATA:
        {json.dumps(case_dict, indent=2)}

        SENTENCING CALCULATOR OUTPUT:
        {json.dumps(sentencing_calc, indent=2)}

        PRE-FETCHED DATA:
        {json.dumps(prefetched, indent=2)}
        """

        # Load layer prompts
        layer_prompts = []
        for i in range(1, 6):
            with open(os.path.join(self.prompts_dir, "layer_prompts", f"layer{i}.md"), "r", encoding="utf-8") as f:
                layer_prompts.append(f.read())

        # 1. Fire 5 Independent Sub-Agents in Parallel!
        logger.info("Spawning 5 independent sub-agents...")
        agent_tasks = [
            self._run_sub_agent(i+1, layer_prompts[i], user_message) 
            for i in range(5)
        ]
        agent_results = await asyncio.gather(*agent_tasks)

        # 2. Orchestrator Synthesis
        # The orchestrator agent takes the results from the 5 sub-agents and creates the final verdict
        logger.info("Running Orchestrator Synthesis...")
        merged_layers = {}
        all_citations = []
        for i, res in enumerate(agent_results):
            layer_key = f"layer{i+1}_result"
            merged_layers[layer_key] = res.get(layer_key, {})
            all_citations.extend(res.get("citations", []))

        orchestrator_prompt = f"""
        You are the Orchestrator Agent. You have received the findings from 5 specialized sub-agents.
        Based on their findings, you must:
        1. Classify the final verdict (CONSISTENT | LENIENT | SIGNIFICANTLY LENIENT | HARSH | SIGNIFICANTLY HARSH | ANOMALOUS)
        2. Set the recommended range based on the Sentencing Calculator output
        3. Write a full reasoning chain synthesizing the sub-agents' findings
        4. Write an executive summary

        SUB-AGENT FINDINGS:
        {json.dumps(merged_layers, indent=2)}

        OUTPUT FORMAT: Valid JSON only.
        {{
          "verdict_classification": "string",
          "recommended_range_min_months": 0,
          "recommended_range_max_months": 0,
          "full_reasoning_chain": "string",
          "summary": "string"
        }}
        """

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": orchestrator_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        try:
            orchestrator_output = json.loads(completion.choices[0].message.content.replace("```json", "").replace("```", "").strip())
        except:
            orchestrator_output = {
                "verdict_classification": "ANOMALOUS",
                "recommended_range_min_months": sentencing_calc.get("cumulative_min", 0),
                "recommended_range_max_months": sentencing_calc.get("cumulative_max", 0),
                "full_reasoning_chain": "Orchestrator synthesis failed.",
                "summary": "Orchestrator synthesis failed."
            }

        # 3. Assemble Final Payload
        final_payload = {
            **merged_layers,
            **orchestrator_output,
            "citations": all_citations
        }
        
        # 4. Confidence Score Calculation
        logger.info("Calculating objective confidence score...")
        confidence = calculate_confidence(final_payload)
        final_payload["confidence_score"] = confidence["score"]
        final_payload["confidence_breakdown"] = confidence["breakdown"]
        
        return final_payload

# Maintain backward compatibility with main.py
ReasoningPipeline = SwarmReasoningPipeline
