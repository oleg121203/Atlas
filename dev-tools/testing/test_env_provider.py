#!/usr/bin/env python3
"""
Тест завантаження дефолтного провайдера з .env файлу
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_env_loading():
    print("🔧 Тест завантаження дефолтного провайдера з .env")
    print("=" * 50)
    
    # 1. Завантажити .env як це робить main.py
    from dotenv import load_dotenv
    print("📁 Завантажуємо .env файл...")
    load_dotenv()
    
    # 2. Перевірити змінні середовища
    print("\n🌍 Змінні середовища після завантаження .env:")
    provider_env = os.getenv('DEFAULT_LLM_PROVIDER', 'НЕ ЗНАЙДЕНО')
    model_env = os.getenv('DEFAULT_LLM_MODEL', 'НЕ ЗНАЙДЕНО')
    print(f"   DEFAULT_LLM_PROVIDER: {provider_env}")
    print(f"   DEFAULT_LLM_MODEL: {model_env}")
    
    # 3. Перевірити ConfigManager
    print("\n⚙️ ConfigManager (як в програмі):")
    from config_manager import ConfigManager
    config = ConfigManager()
    
    provider_config = config.get_current_provider()
    model_config = config.get_current_model()
    print(f"   get_current_provider(): {provider_config}")
    print(f"   get_current_model(): {model_config}")
    
    # 4. Перевірити API ключі
    print("\n🔑 API ключі:")
    gemini_key = config.get_gemini_api_key()
    mistral_key = config.get_mistral_api_key()
    print(f"   Gemini: {'✓ Є' if gemini_key else '✗ Немає'}")
    print(f"   Mistral: {'✓ Є' if mistral_key else '✗ Немає'}")
    
    # 5. Тест LLMManager ініціалізації
    print("\n🤖 LLMManager ініціалізація:")
    try:
        from agents.llm_manager import LLMManager
        from agents.token_tracker import TokenTracker
        
        token_tracker = TokenTracker()
        llm_manager = LLMManager(token_tracker=token_tracker, config_manager=config)
        
        print(f"   LLM Manager створено успішно")
        print(f"   Поточний провайдер буде: {provider_config}")
        
    except Exception as e:
        print(f"   ❌ Помилка створення LLM Manager: {e}")
    
    print("\n" + "=" * 50)
    print("📊 ВИСНОВОК:")
    
    if provider_config == "gemini" and gemini_key:
        print("✅ Програма успішно завантажить Gemini як дефолтний провайдер з .env")
        print("✅ API ключ Gemini доступний")
        return True
    else:
        print("⚠️ Можливі проблеми з налаштуваннями")
        return False

if __name__ == "__main__":
    success = test_env_loading()
    if success:
        print("\n🎉 Все готово! Програма буде використовувати налаштування з .env файлу")
    else:
        print("\n⚠️ Потрібна перевірка налаштувань")
