#!/usr/bin/env python3
"""
Тест utils config manager для GUI
"""

import sys
import os
sys.path.append('/workspaces/autoclicker')

def test_utils_config_manager():
    """Тест utils ConfigManager"""
    try:
        from utils.config_manager import ConfigManager
        
        print("✅ Успішний імпорт utils.ConfigManager")
        
        config = ConfigManager()
        print("✅ Створено ConfigManager")
        
        #Тест API ключів
        print("\n🔑 Тестування API ключів:")
        
        openai_key = config.get_openai_api_key()
        print(f"  OpenAI: {'Встановлено' if openai_key else 'Порожньо'}")
        
        gemini_key = config.get_gemini_api_key()
        print(f"  Gemini: {'Встановлено' if gemini_key else 'Порожньо'}")
        
        mistral_key = config.get_mistral_api_key()
        print(f"  Mistral: {'Встановлено' if mistral_key else 'Порожньо'}")
        
        groq_key = config.get_groq_api_key()
        print(f"  Groq: {'Встановлено' if groq_key else 'Порожньо'}")
        
        #Тест get_setting
        print("\n⚙️  Тестування get_setting:")
        
        gemini_via_setting = config.get_setting('gemini_api_key')
        print(f"  get_setting('gemini_api_key'): {'Встановлено' if gemini_via_setting else 'Порожньо'}")
        
        provider = config.get_current_provider()
        print(f"  Поточний провайдер: {provider}")
        
        model = config.get_current_model()
        print(f"  Поточна модель: {model}")
        
        #Тест storage/loading
        print("\n💾 Тестування збереження/завантаження:")
        
        #Тестове settings
        test_settings = {
            'test_setting': 'test_value',
            'api_keys': {
                'gemini': 'test_gemini_key'
            }
        }
        
        config.save(test_settings)
        print("  ✅ Збереження працює")
        
        loaded_settings = config.load()
        print(f"  ✅ Завантаження працює: {len(loaded_settings)} ключів")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Тест utils ConfigManager для GUI")
    print("=" * 50)
    
    success = test_utils_config_manager()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 UTILS CONFIG MANAGER ПРАЦЮЄ!")
        print("✅ GUI тепер повинен працювати правильно")
    else:
        print("❌ Є проблеми з utils config manager")
