#!/usr/bin/env python3
"""
Тест loading ключів та провайдера з .env файлу
"""

import os
from pathlib import Path


def test_env_loading():
    print("🔍 Перевірка завантаження з .env файлу")
    print("=" * 50)

    #1. Перевірити наявність .env файлу
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env файл знайдено: {env_file.absolute()}")

        #Показати вміст
        with open(env_file) as f:
            content = f.read()
        print("📄 Вміст .env файлу:")
        print(content)
    else:
        print("❌ .env файл НЕ знайдено!")
        return False

    print("\n" + "=" * 50)

    #2. Завантажити .env
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv імпортовано")

        load_dotenv()
        print("✅ .env файл завантажено")
    except ImportError:
        print("❌ python-dotenv не встановлено")
        return False
    except Exception as e:
        print(f"❌ Помилка завантаження .env: {e}")
        return False

    #3. Перевірити змінні середовища
    print("\n🔑 Перевірка API ключів:")
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    }

    for key, value in api_keys.items():
        if value:
            #Приховати ключ, показати тільки перші та останні символи
            if len(value) > 10:
                display = f"{value[:8]}...{value[-4:]}"
            else:
                display = "***"
            print(f"✅ {key}: {display}")
        else:
            print(f"❌ {key}: НЕ встановлено")

    print("\n⚙️ Перевірка налаштувань:")
    settings = {
        "DEFAULT_LLM_PROVIDER": os.getenv("DEFAULT_LLM_PROVIDER"),
        "DEFAULT_LLM_MODEL": os.getenv("DEFAULT_LLM_MODEL"),
    }

    for key, value in settings.items():
        if value:
            print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: НЕ встановлено")

    print("\n" + "=" * 50)

    #4. Тестувати ConfigManager
    print("🔧 Тестування ConfigManager:")
    try:
        from config_manager import ConfigManager
        config = ConfigManager()
        print("✅ ConfigManager створено")

        #Тестувати методи getting ключів
        print("\n📋 Методи ConfigManager:")

        gemini_key = config.get_gemini_api_key()
        if gemini_key:
            display = f"{gemini_key[:8]}...{gemini_key[-4:]}" if len(gemini_key) > 10 else "***"
            print(f"✅ get_gemini_api_key(): {display}")
        else:
            print("❌ get_gemini_api_key(): порожній")

        mistral_key = config.get_mistral_api_key()
        if mistral_key:
            display = f"{mistral_key[:8]}...{mistral_key[-4:]}" if len(mistral_key) > 10 else "***"
            print(f"✅ get_mistral_api_key(): {display}")
        else:
            print("❌ get_mistral_api_key(): порожній")

        provider = config.get_current_provider()
        print(f"✅ get_current_provider(): {provider}")

        model = config.get_current_model()
        print(f"✅ get_current_model(): {model}")

    except Exception as e:
        print(f"❌ Помилка ConfigManager: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n🎯 Висновок:")

    #Підрахувати, скільки ключів встановлено
    valid_keys = sum(1 for v in api_keys.values() if v and v not in ["", "your_real_gemini_key_here", "your_real_mistral_key_here", "your_real_groq_key_here"])
    total_keys = len(api_keys)

    if valid_keys > 0:
        print(f"✅ {valid_keys}/{total_keys} API ключів встановлено правильно")
        if settings["DEFAULT_LLM_PROVIDER"]:
            print(f"✅ Дефолтний провайдер: {settings['DEFAULT_LLM_PROVIDER']}")
        if settings["DEFAULT_LLM_MODEL"]:
            print(f"✅ Дефолтна модель: {settings['DEFAULT_LLM_MODEL']}")
        print("🚀 .env файл працює правильно!")
        return True
    print("⚠️ Немає дійсних API ключів")
    print("💡 Відредагуйте .env файл та додайте справжні ключі")
    return False

if __name__ == "__main__":
    test_env_loading()
