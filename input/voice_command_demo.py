import os
import sys

# Add the parent directory to the path so we can import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from input.voice_command_parser import VoiceCommandParser

def demonstrate_voice_command_parser():
    """Demonstrate the voice command parser functionality"""
    print("Initializing Voice Command Parser...")
    parser = VoiceCommandParser()
    
    print("\nCalibrating microphone for ambient noise...")
    parser.calibrate_microphone(duration=5)
    
    print("\nReady to listen for voice commands.")
    print("Try saying phrases like:")
    print("- 'Create workflow data pipeline'")
    print("- 'Open dashboard sales'")
    print("- 'Start task urgent project'")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            command_text = parser.listen_for_command(timeout=5, phrase_time_limit=10)
            if command_text:
                print(f"\nRecognized command: '{command_text}'")
                parsed_command = parser.parse_command(command_text)
                print(f"Parsed action: {parsed_command['action']}")
                if parsed_command['parameters']:
                    print(f"Parameters: {parsed_command['parameters']}")
            else:
                print("No command recognized, listening again...")
    except KeyboardInterrupt:
        print("\nVoice command demo terminated by user.")

if __name__ == "__main__":
    demonstrate_voice_command_parser()
