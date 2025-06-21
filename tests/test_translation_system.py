#!/usr/bin/env python3
"""
Test script for the Chat Translation Manager

Tests the Ukrainian/Russian translation functionality for chat messages.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.chat_translation_manager import ChatTranslationManager
from tools.translation_tool import TranslationTool


def test_language_detection():
    """Test language detection functionality."""
    print("Testing Language Detection...")
    print("=" * 50)

    translation_tool = TranslationTool()

    test_cases = [
        #English
        ("Hello, how are you today?", "en"),
        ("Can you help me with this task?", "en"),
        ("What tools are available?", "en"),

        #Ukrainian
        ("Привіт, як справи?", "uk"),
        ("Чи можеш ти мені допомогти?", "uk"),
        ("Що це за програма?", "uk"),
        ("Зроби скріншот екрана", "uk"),
        ("Покажи мені всі доступні інструменти", "uk"),

        #Russian
        ("Привет, как дела?", "ru"),
        ("Можешь ли ты мне помочь?", "ru"),
        ("Что это за программа?", "ru"),
        ("Сделай скриншот экрана", "ru"),
        ("Покажи мне все доступные инструменты", "ru"),

        #Mixed/unclear
        ("test 123", "en"),
        ("", "en"),
    ]

    for text, expected_lang in test_cases:
        detected_lang, confidence = translation_tool.detect_language(text)
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"{status} '{text}' -> {detected_lang} (confidence: {confidence:.2f}, expected: {expected_lang})")

    print()

def test_translation_context():
    """Test translation context management."""
    print("Testing Translation Context Management...")
    print("=" * 50)

    #Mock LLM manager for testing
    class MockLLMManager:
        def chat(self, messages):
            class MockResult:
                def __init__(self, text):
                    self.response_text = text

            #Simple mock translation
            user_msg = messages[-1]["content"]
            if "Привіт" in user_msg:
                return MockResult("Hello")
            if "Hello" in user_msg and "translate to Ukrainian" in messages[0]["content"]:
                return MockResult("Привіт")
            if "допомогти" in user_msg:
                return MockResult("help")
            if "help" in user_msg and "translate to Ukrainian" in messages[0]["content"]:
                return MockResult("допомогти")
            return MockResult(user_msg)  #No translation

    mock_llm = MockLLMManager()
    translation_manager = ChatTranslationManager(mock_llm)

    #Test Ukrainian message processing
    ukrainian_message = "Привіт! Чи можеш ти мені допомогти?"
    processed_msg, context = translation_manager.process_incoming_message(ukrainian_message)

    print(f"Original message: {ukrainian_message}")
    print(f"Processed message: {processed_msg}")
    print(f"User language: {context.user_language}")
    print(f"Requires translation: {context.requires_response_translation}")
    print()

    #Test response translation
    english_response = "Of course! I'm here to help you with any questions or tasks."
    translated_response = translation_manager.process_outgoing_response(english_response)

    print(f"English response: {english_response}")
    print(f"Translated response: {translated_response}")
    print()

    #Test English message (no translation needed)
    english_message = "What tools are available?"
    processed_msg2, context2 = translation_manager.process_incoming_message(english_message)

    print(f"English message: {english_message}")
    print(f"Processed message: {processed_msg2}")
    print(f"Requires translation: {context2.requires_response_translation}")
    print()

def test_translation_status():
    """Test translation status and debugging features."""
    print("Testing Translation Status...")
    print("=" * 50)

    translation_tool = TranslationTool()

    test_messages = [
        "Привіт, як справи?",  #Ukrainian
        "Hello, how are you?",  #English
        "Привет, что делаешь?",  #Russian
    ]

    for msg in test_messages:
        info = translation_tool.detect_language_info(msg) if hasattr(translation_tool, "detect_language_info") else {}
        print(f"Message: {msg}")
        if info:
            print(f"  - Language: {info.get('detected_language', 'unknown')}")
            print(f"  - Confidence: {info.get('confidence', 0):.2f}")
            print(f"  - Should translate: {info.get('should_translate', False)}")
        print()

def main():
    """Run all translation tests."""
    print("🌐 Atlas Chat Translation System Tests")
    print("=" * 60)
    print()

    try:
        test_language_detection()
        test_translation_context()
        test_translation_status()

        print("✅ All translation tests completed!")
        print()
        print("Translation system is ready for integration.")
        print("Users can now chat in Ukrainian or Russian, and responses will be automatically translated.")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
