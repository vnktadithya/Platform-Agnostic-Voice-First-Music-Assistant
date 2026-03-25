# backend/services/speech_to_text.py
import requests
import os
import logging
import io
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class SpeechToTextService:
    @staticmethod
    def transcribe_audio(file_obj) -> str:
        """
        Transcribes audio using Groq's Whisper-large-v3.
        Includes a specialized prompt for phonetic transliteration of 
        non-English song names (Telugu, Hindi, Tamil etc.) into Latin script.
        """
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        
        # TRANS-PHONETIC PROMPT: Forces Whisper to use English letters for foreign sounds.
        prompt_text = (
            "The transcript is strictly in English letters (Latin script). "
            "Even for foreign music terms like Telugu, Tamil, or Hindi song titles, "
            "write them exactly as they sound phonetically in English. "
            "Example: 'Nuvve Nuvve', 'Manasu Palike', 'Tum Hi Ho'. "
            "Never use native scripts like Telugu or Devanagari."
        )

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

        try:
            if isinstance(file_obj, bytes):
                file_tuple = ("audio.wav", io.BytesIO(file_obj), "audio/wav")
            else:
                file_tuple = ("audio.wav", file_obj, "audio/wav")

            files = {"file": file_tuple}
            data = {
                "model": "whisper-large-v3",
                "temperature": "0",
                "response_format": "json",
                "language": "en",
                "prompt": prompt_text
            }
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            if response.status_code != 200:
                logger.error(f"Groq STT Error: {response.text}")
                return ""

            result = response.json()
            transcript = result.get("text", "").strip()
            logger.info(f"Groq Phonetic Transcription: {transcript}")
            return transcript

        except Exception as e:
            logger.error(f"Groq STT failed: {str(e)}", exc_info=True)
            return ""
