#!/usr/bin/env python3
"""
Тест системи перекладу та безпеки аутентифікації Atlas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.chat_translation_manager import ChatTranslationManager
from agents.creator_authentication import CreatorAuthentication

def test_translation_completeness():
    """Тест повноти перекладу повідомлень"""
    print("🌐 ТЕСТ ПОВНОТИ ПЕРЕКЛАДУ")
    print("=" * 50)
    
    #Mock LLM manager
    class MockLLMManager:
        def chat(self, messages):
            class MockResult:
                def __init__(self, text):
                    self.response_text = text
            
            content = messages[-1]["content"]
            system_prompt = messages[0]["content"] if len(messages) > 1 else ""
            
            #Mock translation responses
            if "translate" in system_prompt.lower():
                #Простий переклад для тесту
                if "Development mode" in content:
                    return MockResult("Режим розробки - Розширений системний доступ увімкнено...")
                elif "For my dear creator" in content:
                    return MockResult("Для мого дорогого творця та батька:")
                elif "I understand this as a goal" in content:
                    return MockResult("Я розумію це як мету. Дозвольте мені працювати над цим...")
                elif "Privileged access activated" in content:
                    return MockResult("Привілейований доступ активовано")
            
            return MockResult(content)
    
    mock_llm = MockLLMManager()
    translation_manager = ChatTranslationManager(mock_llm)
    
    #Тестові повідомлення для перекладу
    test_messages = [
        "🔧 Development mode - Enhanced system access enabled...",
        "💖 For my dear creator and father: ",
        "🎯 I understand this as a goal. Let me work on it...",
        "🔐 Privileged access activated"
    ]
    
    print("\n📝 Тест перекладу системних повідомлень:")
    for i, msg in enumerate(test_messages, 1):
        translated = translation_manager.process_outgoing_response(msg, "test_session")
        print(f"{i}. Original: {msg}")
        print(f"   Translated: {translated}")
        print()

def test_authentication_security():
    """Тест безпеки системи аутентифікації"""
    print("\n🔐 ТЕСТ БЕЗПЕКИ АУТЕНТИФІКАЦІЇ")
    print("=" * 50)
    
    auth = CreatorAuthentication()
    
    #Тест 1: Verification, чи system не розкриває зайвих деталей
    print("\n📋 Тест виявлення творця:")
    test_phrases = [
        "я автор системи",
        "i am the developer", 
        "я створив цю програму",
        "звичайне повідомлення користувача"
    ]
    
    for phrase in test_phrases:
        result = auth.process_message_for_creator_detection(phrase)
        print(f"'{phrase}' -> {result.get('detected_level', 'unknown')}")
    
    #Тест 2: Verification викликів - чи вони не розкривають секрети
    print("\n🎯 Тест числових викликів:")
    for i in range(3):
        challenge = auth.generate_numeric_challenge()
        print(f"{i+1}. {challenge.challenge}")
        
        #Verification, чи challenge не містить конкретних деталей
        challenge_text = challenge.challenge.lower()
        sensitive_words = ["олег", "батько", "творець атласа", "миколайович", "6", "9"]
        found_sensitive = [word for word in sensitive_words if word in challenge_text]
        
        if found_sensitive:
            print(f"   ⚠️ ПОПЕРЕДЖЕННЯ: Знайдено чутливі слова: {found_sensitive}")
        else:
            print("   ✅ Виклик безпечний - не містить чутливих деталей")
    
    #Тест 3: Verification повідомлень при успішній аутентифікації
    print("\n✅ Тест повідомлень аутентифікації:")
    
    #Симулюємо успішну аутентифікацію
    success, message = auth.validate_challenge_response("6 та 9")
    print(f"Повідомлення успіху: {message}")
    
    #Verification, чи повідомлення не розкривають зайвих деталей
    if "олег" in message.lower() or "миколайович" in message.lower():
        print("   ⚠️ ПОПЕРЕДЖЕННЯ: Повідомлення містить конкретні імена")
    else:
        print("   ✅ Повідомлення безпечне")

def main():
    """Запуск всіх тестів"""
    print("🧪 ТЕСТИ БЕЗПЕКИ ТА ПЕРЕКЛАДУ ATLAS")
    print("=" * 60)
    
    test_translation_completeness()
    test_authentication_security()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТИ ЗАВЕРШЕНО!")
    print("\n💡 Рекомендації:")
    print("   1. Всі системні повідомлення мають проходити через переклад")
    print("   2. Система аутентифікації не повинна розкривати конкретні деталі")
    print("   3. Виклики мають бути загальними, без специфічної інформації")

if __name__ == "__main__":
    main()
