#!/usr/bin/env python3
"""
Тест інтеграції основних компонентів Atlas

Цей скрипт перевіряє основні функції:
1. CreatorAuthentication з методом process_message_for_creator_detection
2. Форматувальні функції в ChatContextManager
3. Система перекладу
"""

import os
import sys

# Додаємо шлях до Atlas (два рівні вгору від dev-tools/testing/)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def test_creator_authentication():
    """Тестування системи аутентифікації творця"""
    print("🔐 Тестування CreatorAuthentication...")

    from agents.creator_authentication import CreatorAuthentication

    auth = CreatorAuthentication()

    # Тест 1: Перевірка методу process_message_for_creator_detection
    test_messages = [
        "Привіт, я творець Atlas",
        "Я розробив цю систему",
        "Звичайне повідомлення користувача",
    ]

    print("  📋 Тест виявлення творця:")
    for msg in test_messages:
        try:
            result = auth.process_message_for_creator_detection(msg)
            print(f"    ✅ '{msg[:30]}...' -> {result}")
        except Exception as e:
            print(f"    ❌ Помилка: {e}")
            return False

    # Тест 2: Емоційні відповіді (якщо є активна сесія)
    print("  💖 Тест емоційних відповідей:")
    try:
        response = auth.get_creator_emotional_response("greeting")
        print(f"    ✅ Greeting response: {response[:50]}...")
    except Exception as e:
        print(f"    ⚠️ Емоційні відповіді доступні тільки в активній сесії: {e}")

    return True

def test_formatting_functions():
    """Тестування форматувальних функцій"""
    print("\n📝 Тестування форматувальних функцій...")

    from agents.chat_context_manager import ChatContextManager

    manager = ChatContextManager()

    test_text = "тестовий текст"

    # Тест форматувальних функцій
    tests = [
        ("Bold", manager.format_bold, f"**{test_text}**"),
        ("Italic", manager.format_italic, f"*{test_text}*"),
        ("Code", manager.format_code, f"`{test_text}`"),
        ("Quote", manager.format_quote, f"> {test_text}"),
        ("Link", lambda t: manager.format_link(t, "http://example.com"), f"[{test_text}](http://example.com)"),
    ]

    for name, func, expected in tests:
        try:
            result = func(test_text)
            if result == expected:
                print(f"    ✅ {name}: {result}")
            else:
                print(f"    ❌ {name}: Expected '{expected}', got '{result}'")
                return False
        except Exception as e:
            print(f"    ❌ {name}: Помилка {e}")
            return False

    return True

def test_translation_system():
    """Тестування системи перекладу"""
    print("\n🌐 Тестування системи перекладу...")

    from tools.translation_tool import TranslationTool

    tool = TranslationTool()

    # Тест виявлення мови
    test_texts = [
        ("Привіт, як справи?", "uk"),
        ("Hello, how are you?", "en"),
        ("Привет, как дела?", "ru"),
    ]

    print("  🔍 Тест виявлення мови:")
    for text, expected_lang in test_texts:
        try:
            detected_lang, confidence = tool.detect_language(text)
            if detected_lang == expected_lang:
                print(f"    ✅ '{text}' -> {detected_lang} (confidence: {confidence:.2f})")
            else:
                print(f"    ⚠️ '{text}' -> Expected {expected_lang}, got {detected_lang} (confidence: {confidence:.2f})")
        except Exception as e:
            print(f"    ❌ Помилка: {e}")
            return False

    return True

def main():
    """Основна функція тестування"""
    print("🧪 ЗАПУСК ІНТЕГРАЦІЙНИХ ТЕСТІВ ATLAS")
    print("=" * 50)

    tests = [
        ("CreatorAuthentication", test_creator_authentication),
        ("Formatting Functions", test_formatting_functions),
        ("Translation System", test_translation_system),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🧪 Тестування: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: ПРОЙДЕНО")
                passed += 1
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕНО")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: КРИТИЧНА ПОМИЛКА - {e}")
            failed += 1

    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Не пройдено: {failed}")
    print(f"   📈 Загальний результат: {passed}/{passed + failed}")

    if failed == 0:
        print("🎉 Всі тести пройдено успішно!")
        return True
    print("⚠️ Деякі тести не пройдено. Потрібно виправити помилки.")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
