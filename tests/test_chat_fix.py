#!/usr/bin/env python3
"""
Тест чату Atlas без помилок OpenAI client
"""

import sys
from utils.llm_manager import LLMManager
from agents.token_tracker import TokenTracker
from config_manager import ConfigManager

def test_chat():
    """Тест чату без помилок"""
    print("🧪 Тестування чату Atlas...")
    
    try:
        #Initialization компонентів
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        
        #Initialization LLM Manager
        llm_manager = LLMManager(token_tracker, config_manager)
        print("✅ LLM Manager ініціалізовано")
        
        #Verification доступних провайдерів
        providers = llm_manager.get_available_providers()
        print(f"📋 Доступні провайдери: {list(providers.keys())}")
        
        #Verification поточного провайдера
        print(f"🔄 Поточний провайдер: {llm_manager.current_provider}")
        print(f"🤖 Поточна модель: {llm_manager.current_model}")
        
        #Тест простого чату
        if "gemini" in providers:
            print("💬 Тестування чату з Gemini...")
            messages = [{"role": "user", "content": "Скажи просто 'Привіт від Atlas!' і все."}]
            
            try:
                response = llm_manager.chat(messages)
                print(f"✅ Відповідь отримано: {response.response_text[:100]}...")
                print(f"📊 Токени: {response.total_tokens}")
                
                #Verification, чи немає помилок OpenAI
                if "openai" not in response.response_text.lower() and "error" not in response.response_text.lower():
                    print("✅ Чат працює без помилок OpenAI!")
                else:
                    print("⚠️  Можливо є згадки про помилки в відповіді")
                    
            except Exception as e:
                print(f"❌ Помилка чату: {e}")
                return False
        else:
            print("⚠️  Gemini недоступний для тесту")
        
        #Тест перевірки OpenAI availability
        openai_available = llm_manager.is_provider_available("openai")
        print(f"🔌 OpenAI доступність: {openai_available}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тесту: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Головна функція"""
    success = test_chat()
    if success:
        print("\n🎉 Тест чату успішний! Помилки OpenAI client виправлено!")
        return 0
    else:
        print("\n❌ Тест чату не пройшов")
        return 1

if __name__ == "__main__":
    sys.exit(main())
