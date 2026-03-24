# services/speech_to_text.py
# Production: Google Gemini (Azure-compatible)
# For the original Groq (lowest-latency) version, see speech_to_text.groq.py
import os
import base64
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class SpeechToTextService:
    @staticmethod
    def transcribe_audio(file_obj) -> str:
        """
        Transcribes audio using Google Gemini's multimodal capabilities.
        Accepts a file-like object (bytesIO or UploadFile.file) directly.
        
        Gemini natively transliterates foreign words (Telugu, Hindi, Tamil, etc.)
        into English alphabets exactly as they sound, without translating meaning.
        
        For local development with even lower latency, swap to speech_to_text.groq.py
        which uses Groq's LPU-powered Whisper-large-v3.
        """
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing. Get a free key from https://aistudio.google.com/app/apikey and add it to your .env file.")

        try:
            
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Read the audio bytes
            if isinstance(file_obj, bytes):
                audio_bytes = file_obj
            else:
                audio_bytes = file_obj.read()
            
            # Transliteration prompt: output must be in English letters ONLY
            prompt_text = (
                "Transcribe this audio into English text. "
                "If the speaker uses any non-English words (like Telugu, Hindi, Tamil, Spanish, etc.), "
                "transliterate those words into English alphabets exactly as they sound. "
                "Do NOT translate the meaning. Just write how the words sound in English letters. "
                "Example: If someone says a Telugu song name, write it as 'nuvvu nenantu' not the Telugu script. "
                "Output ONLY the transcribed text, nothing else. No quotes, no explanations."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt_text,
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=1024,
                )
            )
            
            transcript = response.text.strip()
            
            logger.info(f"Gemini Transcription: {transcript}")
            return transcript

        except Exception as e:
            logger.error(f"Gemini STT failed: {str(e)}", exc_info=True)
            raise e
