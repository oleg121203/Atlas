"""
Voice Assistant Plugin for Atlas

This plugin provides voice recognition and text-to-speech capabilities.
"""

import json
import logging
import threading
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class VoiceAssistantPlugin:
    """Voice assistant plugin for Atlas."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.is_initialized = False
        
        # Voice settings
        self.voice_rate = self.config.get("voice_rate", 150)
        self.voice_volume = self.config.get("voice_volume", 0.8)
        self.language = self.config.get("language", "en-US")
    
    def initialize(self, llm_manager=None, atlas_app=None, agent_manager=None) -> bool:
        """Initialize the plugin."""
        try:
            # Initialize text-to-speech
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.voice_rate)
                self.tts_engine.setProperty('volume', self.voice_volume)
                logger.info("Text-to-speech engine initialized")
            except ImportError:
                logger.warning("pyttsx3 not available, text-to-speech disabled")
            
            # Initialize speech recognition
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("Speech recognition initialized")
            except ImportError:
                logger.warning("speech_recognition not available, speech recognition disabled")
            
            self.is_initialized = True
            logger.info("Voice assistant plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize voice assistant plugin: {e}")
            return False
    
    def speak_text(self, text: str) -> Dict[str, Any]:
        """Convert text to speech."""
        try:
            if not self.is_initialized or not self.tts_engine:
                return {
                    "success": False,
                    "error": "Text-to-speech not available"
                }
            
            # Run TTS in a separate thread to avoid blocking
            def speak():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    logger.error(f"TTS error: {e}")
            
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
            
            return {
                "success": True,
                "data": {"text": text},
                "message": f"Speaking: {text[:50]}..."
            }
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def listen_for_speech(self, timeout: int = 5) -> Dict[str, Any]:
        """Listen for speech and convert to text."""
        try:
            if not self.is_initialized or not self.recognizer or not self.microphone:
                return {
                    "success": False,
                    "error": "Speech recognition not available"
                }
            
            with self.microphone as source:
                logger.info("Listening for speech...")
                try:
                    audio = self.recognizer.listen(source, timeout=timeout)
                    
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    
                    return {
                        "success": True,
                        "data": {"text": text},
                        "message": f"Recognized: {text}"
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Speech recognition failed: {str(e)}"
                    }
            
        except Exception as e:
            logger.error(f"Speech listening failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """Transcribe audio file to text."""
        try:
            if not self.is_initialized or not self.recognizer:
                return {
                    "success": False,
                    "error": "Speech recognition not available"
                }
            
            import speech_recognition as sr
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio, language=self.language)
                
                return {
                    "success": True,
                    "data": {"text": text, "file": audio_file},
                    "message": f"Transcribed audio file: {audio_file}"
                }
                
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def voice_command(self, command: str) 