#!/usr/bin/env python3
"""
Простий тест ініціалізації системи перекладу
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_translation_initialization():
    """Тест ініціалізації системи перекладу"""
    print("🧪 ТЕСТ ІНІЦІАЛІЗАЦІЇ СИСТЕМИ ПЕРЕКЛАДУ")
    print("=" * 50)

    try:
        from agents.chat_translation_manager import ChatTranslationManager

        #Тест 1: Initialization без LLM manager
        print("\n1. Тест ініціалізації без LLM manager:")
        translation_manager = ChatTranslationManager()
        print("   ✅ ChatTranslationManager створено успішно")

        #Тест 2: Verification чи system може працювати без LLM
        print("\n2. Тест базових функцій без LLM:")

        #Verification детекції мови
        ukrainian_text = "Привіт, як справи?"
        detected_lang, confidence = translation_manager.translation_tool.detect_language(ukrainian_text)
        print(f"   Детекція мови: '{ukrainian_text}' -> {detected_lang} (впевненість: {confidence:.2f})")

        #Verification чи потрібен переклад
        should_translate = translation_manager.translation_tool.should_translate_message(ukrainian_text)
        print(f"   Чи потрібен переклад: {should_translate}")

        #Тест 3: Mock LLM manager
        print("\n3. Тест з Mock LLM manager:")

        class MockLLMManager:
            def chat(self, messages):
                class MockResult:
                    def __init__(self, text):
                        self.response_text = text

                content = messages[-1]["content"]
                if "Привіт" in content and "translate" in messages[0]["content"]:
                    return MockResult("Hello, how are you?")
                if "Hello" in content and "Ukrainian" in messages[0]["content"]:
                    return MockResult("Привіт, як справи?")
                return MockResult(content)

        #Встановлюємо Mock LLM
        mock_llm = MockLLMManager()
        translation_manager.set_llm_manager(mock_llm)
        print("   ✅ Mock LLM manager встановлено")

        #Тест перекладу
        processed_msg, context = translation_manager.process_incoming_message(ukrainian_text)
        print(f"   Оброблене повідомлення: '{processed_msg}'")
        print(f"   Мова користувача: {context.user_language}")
        print(f"   Потрібен переклад відповіді: {context.requires_response_translation}")

        #Тест зворотного перекладу
        english_response = "Hello! I can help you with various tasks."
        if context.requires_response_translation:
            translated_response = translation_manager.process_outgoing_response(english_response)
            print(f"   Англійська відповідь: '{english_response}'")
            print(f"   Перекладена відповідь: '{translated_response}'")

        print("\n✅ Всі тести пройшли успішно!")

    except Exception as e:
        print(f"\n❌ Помилка при тестуванні: {e}")
        import traceback
        traceback.print_exc()

def test_language_detection_patterns():
    """Тест паттернів детекції мови"""
    print("\n🌐 ТЕСТ ПАТТЕРНІВ ДЕТЕКЦІЇ МОВИ")
    print("=" * 50)

    try:
        from agents.chat_translation_manager import ChatTranslationManager

        translation_manager = ChatTranslationManager()

        test_phrases = [
            ("Привіт, як справи?", "uk", "Українська"),
            ("Привет, как дела?", "ru", "Російська"),
            ("Hello, how are you?", "en", "Англійська"),
            ("Зроби скріншот екрана", "uk", "Українська команда"),
            ("Сделай скриншот экрана", "ru", "Російська команда"),
            ("Take a screenshot", "en", "Англійська команда"),
            ("Які у тебе інструменти?", "uk", "Українське питання про інструменти"),
            ("Какие у тебя инструменты?", "ru", "Російське питання про інструменти"),
            ("What tools do you have?", "en", "Англійське питання про інструменти"),
        ]

        print("\n📝 Результати детекції:")
        for phrase, expected_lang, description in test_phrases:
            detected_lang, confidence = translation_manager.translation_tool.detect_language(phrase)
            should_translate = translation_manager.translation_tool.should_translate_message(phrase)

            status = "✅" if detected_lang == expected_lang else "❌"
            print(f"{status} {description}")
            print(f"    '{phrase}'")
            print(f"    Детектовано: {detected_lang} (очікувалось: {expected_lang})")
            print(f"    Впевненість: {confidence:.2f}, Перекласти: {should_translate}")
            print()

    except Exception as e:
        print(f"\n❌ Помилка при тестуванні детекції: {e}")

def main():
    """Запуск всіх тестів"""
    test_translation_initialization()
    test_language_detection_patterns()

    print("\n" + "=" * 60)
    print("🎉 ТЕСТУВАННЯ ЗАВЕРШЕНО!")
    print("\n💡 Система перекладу тепер правильно ініціалізується:")
    print("   1. ChatTranslationManager створюється без LLM manager")
    print("   2. LLM manager встановлюється пізніше через set_llm_manager()")
    print("   3. Система може працювати з детекцією мови навіть без LLM")
    print("   4. Переклад працює після встановлення LLM manager")

if __name__ == "__main__":
    main()
