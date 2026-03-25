import os
import requests
import json
from dotenv import load_dotenv
import logging
from backend.utils.action_params import ACTION_REQUIRED_PARAMS

load_dotenv()
logger = logging.getLogger(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def call_llm_agent(user_text: str, short_reply: bool = True, action_keys: list = []) -> dict:
    """
    Calls the Groq API (Llama 3.3 70B) to understand user intent for the music assistant.
    Provides sub-second latency for real-time interactions on Azure.
    """
    if not GROQ_API_KEY:
         raise ValueError("GROQ_API_KEY is missing. Please ensure it is set in your .env file.")

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
    prompt = f"""You are SAM(Self-Adaptive Music Assistant), a world-class conversational music assistant.
    ⚠️ IMPORTANT: if user asks to read something aloud, then dont consider the below prompt and just do as the user say.
Your primary job is to understand the user's request and decompose it into the necessary sequence of actions and their parameters.
Instructions:
1. **Analyze the user's request:** Parse and split the request into one or more music-related actions if multiple tasks are stated (e.g., "play X and add it to playlist Y").
2. **Choose Actions:** For each action needed, select from the `Available Actions` list. The order in the list should match the order of intent in the user's message.
3. **Extract Parameters:** For each action, identify the required parameters like `song_name`, `artist`, `playlist_name`, or `mood` where relevant.
4. **Volume Rules**: Always extract volume as an integer (0-100). Use 'absolute', 'increase', or 'decrease' modes.
5. **Handle Non-Music Talk:** If there is only small talk, ignore actions and return just a conversational `reply`.
6. **Use Conversation History:** Check history to infer pronouns like 'this' or 'it'.
7. **JSON Output Only:** Return EXACT JSON schema.
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
Available Actions: {available_actions_prompt}
""" + user_text

    # Groq OpenAI-compatible endpoint
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs strictly in JSON format."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3,
        "max_tokens": 1024
    }
    
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        if resp.status_code != 200:
             logger.error(f"LLM API Error: {resp.text}")
             raise Exception(f"LLM API call failed with status {resp.status_code}: {resp.text}")
             
        response_json = resp.json()
        content = response_json["choices"][0]["message"]["content"]
        result = json.loads(content)
        return result
    except Exception as e:
        logger.exception("Unexpected error during LLM call")
        raise e