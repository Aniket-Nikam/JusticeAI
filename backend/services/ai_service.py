import os
import logging
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)

def get_master_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'master_prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def analyze_case(case_description: str, previous_learnings: str = "") -> str:
    # Use Pydantic settings for validated API key
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    master_prompt = get_master_prompt()
    
    synthesis_prompt = f"""
    CASE DESCRIPTION:
    {case_description}
    
    ---
    PRIOR SYSTEM LEARNINGS (For Consistency):
    {previous_learnings}
    """
    
    logger.info("Starting Llama Reasoning Phase with Groq...")
    
    messages = [
        {"role": "system", "content": master_prompt},
        {"role": "user", "content": synthesis_prompt}
    ]
    
    try:
        # Try primary model
        logger.info("Calling primary model: llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
        )
        logger.info("Llama reasoning complete.")
        return response.choices[0].message.content
        
    except Exception as e:
        logger.warning(f"Primary model failed: {str(e)}. Attempting fallback...")
        try:
            # Try fallback model
            logger.info("Calling fallback model: llama-3.1-8b-instant")
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.2,
            )
            logger.info("Llama reasoning complete (via fallback).")
            return response.choices[0].message.content
        except Exception as fallback_e:
            error_msg = str(fallback_e)
            logger.error(f"Error during AI analysis (both primary and fallback failed): {error_msg}", exc_info=True)
            raise Exception(f"Groq API Error: {error_msg}")
