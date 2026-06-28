import json

import os

class PromptBuilder:
    def __init__(self):
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        
        # Load system prompt and layers
        with open(os.path.join(self.prompts_dir, "system_prompt.md"), "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
            
        self.layer_prompts = []
        for i in range(1, 6):
            with open(os.path.join(self.prompts_dir, "layer_prompts", f"layer{i}.md"), "r", encoding="utf-8") as f:
                self.layer_prompts.append(f.read())
                
        # Combine them
        self.full_system_prompt = self.system_prompt + "\n\n" + "\n\n".join(self.layer_prompts)

    def build_case_prompt(self, case_dict: dict, prefetched_data: dict, sentencing_calc: dict) -> dict:
        """
        Constructs the final prompt string by injecting data.
        """
        
        case_json = json.dumps(case_dict, indent=2)
        prefetched_json = json.dumps(prefetched_data, indent=2)
        calc_json = json.dumps(sentencing_calc, indent=2)

        user_message = f"""
        CASE DATA:
        {case_json}

        SENTENCING CALCULATOR OUTPUT:
        {calc_json}

        PRE-FETCHED DATA (USE THIS TO GROUND YOUR ANALYSIS):
        {prefetched_json}
        """

        return {
            "system": self.full_system_prompt,
            "user": user_message
        }
