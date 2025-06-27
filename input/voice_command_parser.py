import importlib.util
from typing import Optional

# Check if required modules are available
PY_AUDIO_AVAILABLE = False
speech_recognition_spec = importlib.util.find_spec("speech_recognition")
pyaudio_spec = importlib.util.find_spec("pyaudio")

if speech_recognition_spec and pyaudio_spec:
    import speech_recognition as sr

    PY_AUDIO_AVAILABLE = True
else:
    print(
        "Warning: pyaudio or speech_recognition not available. Voice command functionality will be disabled."
    )


class VoiceCommandParser:
    """Class to parse voice commands using on-device speech-to-text"""

    def __init__(self, language: str = "en-US", energy_threshold: int = 300):
        """Initialize the voice command parser

        Args:
            language (str): Language code for speech recognition
            energy_threshold (int): Energy level for listening detection
        """
        if PY_AUDIO_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.recognizer.energy_threshold = energy_threshold
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
        else:
            self.recognizer = None
            self.microphone = None
        self.language = language
        self.energy_threshold = energy_threshold
        self.is_calibrated = False

    def calibrate_microphone(self, duration: int = 5):
        """Calibrate microphone for ambient noise

        Args:
            duration (int): Duration in seconds to adjust for noise
        """
        if not PY_AUDIO_AVAILABLE:
            print("Microphone calibration skipped - pyaudio not available")
            return

        print("Calibrating microphone... Please wait.")
        if PY_AUDIO_AVAILABLE:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        self.is_calibrated = True
        print("Microphone calibration complete.")

    def listen_for_command(
        self, timeout: int = 5, phrase_time_limit: Optional[int] = None
    ) -> Optional[str]:
        """Listen for a voice command

        Args:
            timeout (int): Seconds to wait for start of phrase
            phrase_time_limit (Optional[int]): Max seconds for phrase duration

        Returns:
            Optional[str]: Transcribed voice command or None if failed
        """
        if not PY_AUDIO_AVAILABLE:
            print("Voice command listening disabled - pyaudio not available")
            return None

        if not self.is_calibrated:
            self.calibrate_microphone()

        print("Listening for command...")
        if PY_AUDIO_AVAILABLE:
            with self.microphone as source:
                try:
                    audio = self.recognizer.listen(
                        source, timeout=timeout, phrase_time_limit=phrase_time_limit
                    )
                    print("Processing audio...")
                    try:
                        # Using Sphinx for offline speech recognition
                        return self.recognizer.recognize_sphinx(
                            audio, language=self.language
                        )
                    except sr.UnknownValueError:
                        print("Could not understand the audio")
                        return None
                    except sr.RequestError as e:
                        print(f"Speech recognition error: {e}")
                        return None
                except sr.WaitTimeoutError:
                    print("No command detected within timeout")
                    return None

    def parse_command(self, command_text):
        """Parse the recognized command text into a structured action"""
        if not command_text:
            return {"action": "no_command", "parameters": {}}

        command_text = command_text.lower().strip()

        # Check for specific command patterns
        if command_text.startswith("create workflow"):
            workflow_name = command_text.replace("create workflow", "").strip()
            if not workflow_name:
                from datetime import datetime

                workflow_name = f"Workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return {"action": "create_workflow", "parameters": {"name": workflow_name}}
        elif command_text.startswith("start task"):
            task_name = command_text.replace("start task", "").strip()
            return {
                "action": "start_task",
                "parameters": {"name": task_name if task_name else "Unnamed Task"},
            }
        elif command_text in ["open dashboard", "show dashboard", "go to dashboard"]:
            return {
                "action": "open_dashboard",
                "parameters": {"name": "main dashboard"},
            }
        elif command_text in ["stop listening", "stop voice command", "disable voice"]:
            return {"action": "stop_listening", "parameters": {}}
        else:
            return {"action": "unknown_command", "parameters": {"text": command_text}}
