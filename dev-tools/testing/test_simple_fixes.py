#!/usr/bin/env python3
"""
Простий тест для перевірки виправлень з API ключами.
"""

import sys

sys.path.append("/Users/dev/Documents/autoclicker")

from utils.config_manager import ConfigManager


def test_api_keys_saving():
    """Тест storage та loading API ключів."""
    print("🔧 Тестування збереження/завантаження API ключів...")

    config_manager = ConfigManager()

    #Створимо тестові settings
    test_settings = {
        "api_keys": {
            "openai": "test_openai_key",
            "gemini": "test_gemini_key",
            "anthropic": "test_anthropic_key",
            "groq": "test_groq_key",
            "mistral": "test_mistral_key",
        },
        "current_provider": "gemini",
    }

    #Збережемо
    config_manager.save(test_settings)
    print("✅ Налаштування збережено")

    #Завантажимо знову
    loaded_settings = config_manager.load()

    #Перевіримо, чи всі ключі на місці
    api_keys = loaded_settings.get("api_keys", {})

    expected_keys = ["openai", "gemini", "anthropic", "groq", "mistral"]
    for key in expected_keys:
        if key in api_keys:
            print(f"✅ {key}: {api_keys[key]}")
        else:
            print(f"❌ {key}: НЕ ЗНАЙДЕНО")

    #Перевіримо провайдер
    provider = loaded_settings.get("current_provider", "")
    print(f"🎯 Провайдер: {provider}")

    #Тест методів getting ключів
    print("\n🔑 Тестування методів отримання ключів:")
    print(f"  openai: {config_manager.get_openai_api_key()}")
    print(f"  gemini: {config_manager.get_gemini_api_key()}")
    print(f"  groq: {config_manager.get_groq_api_key()}")
    print(f"  mistral: {config_manager.get_mistral_api_key()}")

    return loaded_settings

if __name__ == "__main__":
    print("🚀 Запуск тестів для перевірки виправлень з API ключами...")
    print("=" * 60)

    #Тест API ключів
    settings = test_api_keys_saving()

    print("\n" + "=" * 60)
    print("🏁 Тести завершено!")
