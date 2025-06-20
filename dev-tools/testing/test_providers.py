#!/usr/bin/env python3
"""
Тест LLMManager для перевірки доступних провайдерів.
"""

import sys
sys.path.append('/Users/dev/Documents/autoclicker')

from utils.config_manager import ConfigManager

#Імпортуємо тільки частину LLMManager, що нас цікавить
def test_provider_availability():
    """Тест доступності провайдерів без ініціалізації memory manager."""
    print("🤖 Тестування доступності провайдерів...")
    
    config_manager = ConfigManager()
    
    #Перевіримо, які ключі доступні
    providers_with_keys = []
    
    if config_manager.get_openai_api_key():
        providers_with_keys.append("openai")
    
    if config_manager.get_gemini_api_key():
        providers_with_keys.append("gemini")
        
    if config_manager.get_setting('groq_api_key'):
        providers_with_keys.append("groq")
        
    if config_manager.get_setting('mistral_api_key'):
        providers_with_keys.append("mistral")
    
    #Ollama завжди доступний (локальний)
    providers_with_keys.append("ollama")
    
    print(f"🎯 Провайдери з доступними ключами: {providers_with_keys}")
    
    return providers_with_keys

if __name__ == "__main__":
    print("🚀 Тестування провайдерів...")
    print("=" * 50)
    
    providers = test_provider_availability()
    
    print("\n" + "=" * 50)
    print("🏁 Тест завершено!")
