#!/usr/bin/env python3
"""
Тест завантаження .env файлу та API ключів
"""

import os
from pathlib import Path

def test_env_loading():
    print("🧪 Тестування завантаження .env файлу")
    print("=" * 50)
    
    # Імпорт та завантаження
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv імпортовано")
        
        # Завантажити .env
        env_file = Path('.env')
        if env_file.exists():
            print(f"✅ .env файл знайдено: {env_file.absolute()}")
            load_dotenv()
            print("✅ .env файл завантажено")
        else:
            print("❌ .env файл не знайдено")
            return False
            
        # Перевірити ключі
        keys_to_check = [
            "OPENAI_API_KEY",
            "GEMINI_API_KEY", 
            "GROQ_API_KEY",
            "MISTRAL_API_KEY",
            "DEFAULT_LLM_PROVIDER",
            "DEFAULT_LLM_MODEL"
        ]
        
        found_keys = []
        for key in keys_to_check:
            value = os.getenv(key, '')
            if value:
                # Не показувати повні ключі
                if 'API_KEY' in key:
                    display_value = f"{value[:8]}..." if len(value) > 8 else value
                else:
                    display_value = value
                print(f"✅ {key}: {display_value}")
                found_keys.append(key)
            else:
                print(f"❌ {key}: не встановлено")
        
        print(f"\n📊 Знайдено {len(found_keys)} з {len(keys_to_check)} змінних")
        
        # Тест ConfigManager
        print("\n🔧 Тестування ConfigManager...")
        try:
            from config_manager import ConfigManager
            config = ConfigManager()
            print("✅ ConfigManager ініціалізовано")
            
            # Тест методів
            provider = config.get_current_provider()
            model = config.get_current_model()
            gemini_key = config.get_gemini_api_key()
            
            print(f"✅ Провайдер: {provider}")
            print(f"✅ Модель: {model}")
            print(f"✅ Gemini ключ: {'встановлено' if gemini_key else 'не встановлено'}")
            
        except Exception as e:
            print(f"❌ Помилка ConfigManager: {e}")
            return False
            
        return len(found_keys) > 0
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_env_loading()
    if success:
        print("\n🎉 Тест пройдено успішно!")
        print("🚀 Atlas готовий до запуску!")
    else:
        print("\n⚠️  Знайдено проблеми. Перевірте конфігурацію.")
