#!/usr/bin/env python3
"""
Тест виправлень системи режимів Atlas
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.agents.chat_context_manager import ChatContextManager
from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
from modules.agents.token_tracker import TokenTracker
from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


def test_mode_fixes():
    """Тест виправлень режимів"""

    print("🔧 Тестування виправлень системи режимів Atlas")
    print("=" * 60)

    #Initialization
    config_manager = ConfigManager()
    token_tracker = TokenTracker()
    llm_manager = LLMManager(token_tracker)
    memory_manager = EnhancedMemoryManager(llm_manager, config_manager)

    chat_manager = ChatContextManager(memory_manager=memory_manager)

    #Тестові повідомлення
    test_cases = [
        #Очікуємо CASUAL_CHAT
        ("Привіт", "CASUAL_CHAT", "Простий привіт"),
        ("Hi", "CASUAL_CHAT", "Англійський привіт"),
        ("Як справи?", "CASUAL_CHAT", "Звичайне питання"),
        ("Дякую", "CASUAL_CHAT", "Подяка"),
        ("Погода хороша", "CASUAL_CHAT", "Загальна розмова"),

        #Очікуємо SYSTEM_HELP (тільки специфічні питання про Atlas)
        ("Розкажи про Atlas", "SYSTEM_HELP", "Питання про систему"),
        ("Які можливості у Atlas?", "SYSTEM_HELP", "Питання про можливості"),
        ("Explain Atlas modes", "SYSTEM_HELP", "Режими Atlas"),
        ("About your memory", "SYSTEM_HELP", "Про пам'ять системи"),

        #Очікуємо GOAL_SETTING
        ("Зроби скріншот", "GOAL_SETTING", "Завдання"),
        ("Take a screenshot", "GOAL_SETTING", "Завдання англійською"),
        ("Open calculator", "GOAL_SETTING", "Відкрити програму"),

        #Очікуємо CASUAL_CHAT (НЕ SYSTEM_HELP)
        ("яка погода зараз у Львові?", "CASUAL_CHAT", "Питання про погоду - НЕ системне"),
        ("What's the weather like?", "CASUAL_CHAT", "Погода англійською"),
        ("Як дела?", "CASUAL_CHAT", "Загальне питання"),
        ("Tell me a joke", "CASUAL_CHAT", "Розваги"),
    ]

    correct = 0
    total = len(test_cases)

    for i, (message, expected, description) in enumerate(test_cases, 1):
        context = chat_manager.analyze_message(message)
        detected = context.mode.value.upper()
        confidence = context.confidence

        status = "✅" if detected == expected else "❌"
        if detected == expected:
            correct += 1

        print(f'{i:2d}. {status} "{message}"')
        print(f"     Очікувано: {expected}")
        print(f"     Виявлено:  {detected} (впевненість: {confidence:.3f})")
        print(f"     Опис: {description}")

        if detected != expected:
            print(f"     ⚠️  ПОМИЛКА: Очікувався {expected}, отримано {detected}")
        print()

    print("=" * 60)
    print(f"📊 РЕЗУЛЬТАТИ: {correct}/{total} ({100*correct/total:.1f}%) правильних визначень")

    if correct == total:
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНО! Система режимів працює правильно.")
    elif correct >= total * 0.8:
        print("✅ ДОБРИЙ РЕЗУЛЬТАТ! Більшість тестів пройдено.")
    else:
        print("⚠️  ПОТРІБНІ ДОДАТКОВІ ВИПРАВЛЕННЯ.")

    #Тест скидання контексту
    print("\n🔄 Тестування скидання контексту...")
    chat_manager.reset_context()
    print("✅ Контекст скинуто")

    #Тест примусового режиму
    print("\n🎯 Тестування примусового casual режиму...")
    chat_manager.force_casual_mode()
    context = chat_manager.analyze_message("system help")  #Зазвичай це SYSTEM_HELP
    print(f"✅ Після force_casual_mode: {context.mode.value} (має бути casual_chat)")

if __name__ == "__main__":
    test_mode_fixes()
