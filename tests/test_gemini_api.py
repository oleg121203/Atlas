#!/usr/bin/env python3
"""
Простий тест Gemini API для перевірки роботи чату
"""

import os
import sys
from pathlib import Path

#Додаємо поточну директорію до шляху
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_chat():
    """Тестуємо Gemini чат"""
    print("🧪 Тестування Gemini API...")
    
    try:
        #Імпортуємо необхідні класи
        from agents.token_tracker import TokenTracker, TokenUsage
        from agents.llm_manager import LLMManager
        
        #Створюємо token tracker
        token_tracker = TokenTracker()
        
        #Створюємо LLM manager
        llm_manager = LLMManager(token_tracker)
        
        #Перевіряємо, чи Gemini клієнт ініціалізовано
        if not llm_manager.gemini_client:
            print("❌ Gemini клієнт не ініціалізовано")
            return False
        
        print("✅ Gemini клієнт ініціалізовано")
        
        #Тестуємо простий чат
        test_messages = [
            {"role": "user", "content": "Привіт! Скажи щось українською мовою."}
        ]
        
        print("📤 Відправляємо тестове повідомлення...")
        
        #Викликаємо чат
        try:
            response = llm_manager._chat_gemini(test_messages)
            print(f"✅ Отримано відповідь: {response.response_text[:100]}...")
            print(f"📊 Токени: prompt={response.prompt_tokens}, completion={response.completion_tokens}")
            return True
            
        except Exception as e:
            print(f"❌ Помилка чату: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка імпорту або ініціалізації: {e}")
        return False

def test_config():
    """Тестуємо конфігурацію"""
    print("\n🔧 Тестування конфігурації...")
    
    #Перевіряємо config.ini
    if not os.path.exists('config.ini'):
        print("❌ config.ini не знайдено")
        return False
    
    print("✅ config.ini знайдено")
    
    #Перевіряємо .env
    if not os.path.exists('.env'):
        print("❌ .env не знайдено")
        return False
    
    print("✅ .env знайдено")
    
    #Перевіряємо змінні середовища
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key.startswith('your-'):
        print("❌ GEMINI_API_KEY не налаштовано")
        return False
    
    print("✅ GEMINI_API_KEY налаштовано")
    return True

def main():
    """Головна функція"""
    print("🚀 Atlas Gemini API Test")
    print("=" * 30)
    
    #Перехід до директорії Atlas
    atlas_dir = Path(__file__).parent
    os.chdir(atlas_dir)
    
    #Тестуємо конфігурацію
    if not test_config():
        print("\n❌ Проблеми з конфігурацією")
        return False
    
    #Тестуємо Gemini API
    if test_gemini_chat():
        print("\n🎉 Gemini API працює правильно!")
        return True
    else:
        print("\n❌ Проблеми з Gemini API")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
