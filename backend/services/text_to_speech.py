# backend/services/text_to_speech.py
import requests
import os
import io
import logging
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class TextToSpeechService:
    @staticmethod
    def synthesize_speech(text: str) -> bytes:
        """
        Hybrid TTS Solution:
        1. Primary: Groq Orpheus (Ultra-low latency < 200ms).
        2. Fallback: Edge-TTS (Unlimited Microsoft Neural voices).
        """
        # --- Tier 1: Groq Orpheus (LPU Speed) ---
        if GROQ_API_KEY:
            try:
                url = "https://api.groq.com/openai/v1/audio/speech"
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                body = {
                    "model": "canopylabs/orpheus-v1-english",
                    "voice": "troy", 
                    "response_format": "wav",
                    "input": text
                }
                resp = requests.post(url, headers=headers, json=body, timeout=10)
                if resp.status_code == 200:
                    logger.info("Groq Orpheus TTS success.")
                    return resp.content
                logger.warning(f"Groq TTS Tier 1 failed: {resp.status_code}. Falling back to Edge-TTS.")
            except Exception as e:
                logger.warning(f"Groq TTS Tier 1 error: {e}. Falling back to Edge-TTS.")

        # --- Tier 2: Edge-TTS (Free & Robust) ---
        try:
            import edge_tts
            import nest_asyncio
            nest_asyncio.apply()
            
            async def generate_edge():
                communicate = edge_tts.Communicate(text, "en-US-AndrewNeural")
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            return asyncio.run(generate_edge())
        except Exception as e:
            logger.error(f"Dual-Tier TTS failed: {str(e)}", exc_info=True)
            raise e
