# services/LLM_service.py
# Production: Hugging Face (High-Quota / Azure-Compatible)
# Using Qwen 2.5 72B for state-of-the-art JSON extraction and low-latency reasoning.
import os
import json
import requests
from dotenv import load_dotenv
import logging
from backend.utils.action_params import ACTION_REQUIRED_PARAMS

load_dotenv()
logger = logging.getLogger(__name__)

# New Architecture: Hugging Face Inference API
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
MODEL_ID = "Qwen/Qwen2.5-72B-Instruct"

def call_llm_agent(user_text: str, short_reply: bool = True, action_keys: list = []) -> dict:
    """
    Calls the Hugging Face Inference API to understand user intent.
    Provides ~300 requests/hour free, bypassing Gemini's 20 RPD cap on Azure.
    """
    if not HF_API_TOKEN:
         raise ValueError("HF_API_TOKEN is missing. Add it to your .env file.")
    
    available_actions_list = []
    for action in action_keys:
        required = ACTION_REQUIRED_PARAMS.get(action, [])
        if required:
            formatted = f"{action}({', '.join(required)})"
        else:
            formatted = action
        available_actions_list.append(formatted)

    available_actions_prompt = ", ".join(available_actions_list)

    # Construct System Prompt
    system_prompt = f"""You are SAM(Self-Adaptive Music Assistant), a world-class conversational music assistant.
    ⚠️ IMPORTANT: if user asks to read something aloud, then dont consider the below prompt and just do as the user say.
Your primary job is to understand the user's request and decompose it into the necessary sequence of actions and their parameters.

Available Actions: {available_actions_prompt}

Instructions:
1. **Analyze the user's request:** Parse and split the request into one or more music-related actions if multiple tasks are stated.
2. **Choose Actions:** Select from the `Available Actions` list.
3. **Extract Parameters:** Identify required parameters (song_name, artist, playlist_name, volume, etc.).
4. **Volume Rules**: 
   - absolute: "set to 60", "mute(0)", "max(100)"
   - increase/decrease: "louder", "quieter", "up by 20"
5. **Handle Missing Information:** If a required parameter is missing, return a follow-up question as the `reply` and no `actions`.
6. **JSON Output Only:** Always respond with ONLY a JSON object.

Respond in this EXACT JSON format:
{{
  "intent": "...",
  "emotion": "...",
  "actions": [
    {{
      "action": "...",
      "parameters": {{ "...": "..." }},
      "reply": "..."
    }}
  ],
  "reply": "..."
}}
"""

    # Hugging Face Router API (OpenAI Compatible)
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
        "response_format": { "type": "json_object" }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if resp.status_code != 200:
            logger.error(f"Hugging Face API Error: {resp.text}")
            raise Exception(f"Hugging Face API call failed with status {resp.status_code}: {resp.text}")
        
        response_json = resp.json()
        content = response_json["choices"][0]["message"]["content"]
        
        # Parse JSON
        result = json.loads(content)
        return result

    except Exception as e:
        logger.exception("Unexpected error during LLM call")
        raise e