#!/usr/bin/env python3
"""
Простий тест виправлених режимів без LLM залежностей
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.chat_context_manager import ChatContextManager


def test_mode_fixes_simple():
    """Простий тест виправлених режимів"""

    print("🔧 Простий тест виправлень системи режимів")
    print("=" * 50)

    #Створити без залежностей
    chat_manager = ChatContextManager(memory_manager=None)

    #Тестові повідомлення
    test_cases = [
        #Простий привіт - має бути CASUAL_CHAT
        ("Привіт", "CASUAL_CHAT"),
        ("Hi", "CASUAL_CHAT"),
        ("Hello", "CASUAL_CHAT"),

        #Короткі повідомлення - CASUAL_CHAT
        ("Дякую", "CASUAL_CHAT"),
        ("OK", "CASUAL_CHAT"),
        ("👍", "CASUAL_CHAT"),

        #Питання про погоду - НЕ SYSTEM_HELP
        ("яка погода зараз у Львові?", "CASUAL_CHAT"),
        ("What's the weather?", "CASUAL_CHAT"),

        #Тільки специфічні питання про Atlas - SYSTEM_HELP
        ("What are Atlas capabilities?", "SYSTEM_HELP"),
        ("Tell me about Atlas modes", "SYSTEM_HELP"),
        ("About Atlas system", "SYSTEM_HELP"),

        #Завдання - GOAL_SETTING
        ("Take a screenshot", "GOAL_SETTING"),
        ("Open calculator", "GOAL_SETTING"),
        ("Click on button", "GOAL_SETTING"),
    ]

    correct = 0
    total = len(test_cases)

    for i, (message, expected) in enumerate(test_cases, 1):
        try:
            context = chat_manager.analyze_message(message)
            detected = context.mode.value.upper()
            confidence = context.confidence

            status = "✅" if detected == expected else "❌"
            if detected == expected:
                correct += 1

            print(f'{i:2d}. {status} "{message}"')
            print(f"     Очікувано: {expected}")
            print(f"     Виявлено:  {detected} (впевненість: {confidence:.3f})")

            if detected != expected:
                print("     ⚠️  ПОМИЛКА!")
            print()

        except Exception as e:
            print(f"{i:2d}. ❌ ПОМИЛКА: {e}")
            print()

    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТИ: {correct}/{total} ({100*correct/total:.1f}%) правильних")

    if correct >= total * 0.8:
        print("🎉 ДОБРИЙ РЕЗУЛЬТАТ! Система працює краще.")
    else:
        print("⚠️  ПОТРІБНІ ДОДАТКОВІ ВИПРАВЛЕННЯ.")

    #Тест скидання
    print("\n🔄 Тестування скидання...")
    try:
        chat_manager.reset_context()
        print("✅ Скидання працює")
    except Exception as e:
        print(f"❌ Помилка скидання: {e}")

if __name__ == "__main__":
    test_mode_fixes_simple()
