# services/text_to_speech.py
# Production: Google Gemini TTS (Azure-compatible)
# For the original Groq (lowest-latency) version, see text_to_speech.groq.py
import os
import io
import wave
import struct
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class TextToSpeechService:
    @staticmethod
    def synthesize_speech(text: str) -> bytes:
        """
        Synthesizes speech using Google Gemini's TTS capabilities.
        Returns raw audio bytes (WAV) without writing to disk.
        
        For local development with even lower latency, swap to text_to_speech.groq.py
        which uses Groq's LPU-powered Orpheus TTS.
        """
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing. Get a free key from https://aistudio.google.com/app/apikey and add it to your .env file.")

        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Kore"
                            )
                        )
                    ),
                ),
            )
            
            # Extract audio data from response
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            
            # The Gemini TTS API returns raw PCM 24kHz 16-bit mono audio
            # We need to wrap it in a WAV header for browser playback
            sample_rate = 24000
            num_channels = 1
            sample_width = 2  # 16-bit = 2 bytes
            
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)
            
            wav_bytes = wav_buffer.getvalue()
            logger.info(f"Gemini TTS generated {len(wav_bytes)} bytes of audio")
            return wav_bytes

        except Exception as e:
            logger.error("Gemini text-to-speech synthesis failed", exc_info=True)
            raise e
