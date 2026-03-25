# services/text_to_speech.py
# High-Quota Production Version: Edge TTS
# Provides unlimited, high-quality Microsoft Neural voices without API keys or daily quotas.
import os
import io
import asyncio
import logging
import edge_tts
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TextToSpeechService:
    @staticmethod
    def synthesize_speech(text: str) -> bytes:
        """
        Synthesizes speech using Microsoft's Edge TTS engine.
        Returns raw audio bytes (MP3 format which browsers handle better than raw WAV).
        
        This is the preferred high-quota solution for the 2026 free tier.
        """
        try:
            # You can change the voice here. 
            # Examples: en-US-AvaNeural, en-US-AndrewNeural, te-IN-ShrutiNeural (Telugu)
            VOICE = "en-US-AndrewNeural"
            
            # edge-tts is asynchronous, so we run it in the event loop
            async def generate():
                communicate = edge_tts.Communicate(text, VOICE)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            # Check if there is already a running loop (common in FastAPI/Uvicorn)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If in an async context, we need to handle this differently
                    # But for now, since synthesize_speech is called synchronously 
                    # from the worker/beat, we use a new thread or nested loop
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(generate())
                else:
                    return loop.run_until_complete(generate())
            except Exception:
                return asyncio.run(generate())

        except Exception as e:
            logger.error("Edge text-to-speech synthesis failed", exc_info=True)
            raise e
