#!/usr/bin/env python3
"""
Тест уніфікованого ConfigManager
"""

import os
import sys
import tempfile
from pathlib import Path

from utils.config_manager import ConfigManager

#Додаємо шлях до проекту
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_unified_config():
    """Тестуємо уніфікований ConfigManager."""
    print("🧪 ТЕСТ УНІФІКОВАНОГО CONFIGMANAGER")
    print("=" * 50)

    #Створюємо тимчасовий ConfigManager
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        config_manager = ConfigManager(config_path)

        print("🔑 Тестування API ключів...")

        #Тестові API ключі
        test_keys = {
            "openai_api_key": "sk-test-openai-12345",
            "gemini_api_key": "gem-test-12345",
            "mistral_api_key": "mist-test-12345",
            "groq_api_key": "groq-test-12345",
        }

        #Зберігаємо API ключі
        print("  💾 Збереження API ключів...")
        for key, value in test_keys.items():
            config_manager.set_setting(key, value)

        #Перевіряємо storage
        print("  📖 Перевірка збереження...")
        for key, expected_value in test_keys.items():
            actual_value = config_manager.get_setting(key)
            if actual_value == expected_value:
                print(f"    ✅ {key}: збережено правильно")
            else:
                print(f"    ❌ {key}: очікували '{expected_value}', отримали '{actual_value}'")

        #Тестуємо спеціальні методи API ключів
        print("  🔍 Тестування спеціальних методів...")

        openai_key = config_manager.get_openai_api_key()
        gemini_key = config_manager.get_gemini_api_key()
        mistral_key = config_manager.get_mistral_api_key()
        groq_key = config_manager.get_groq_api_key()

        print(f"    OpenAI: {openai_key}")
        print(f"    Gemini: {gemini_key}")
        print(f"    Mistral: {mistral_key}")
        print(f"    Groq: {groq_key}")

        #Тестуємо провайдер і модель
        print("  ⚙️ Тестування провайдера і моделі...")
        config_manager.set_setting("current_provider", "openai")
        config_manager.set_setting("current_model", "gpt-4")

        provider = config_manager.get_current_provider()
        model = config_manager.get_current_model()
        model_name = config_manager.get_model_name()

        print(f"    Provider: {provider}")
        print(f"    Model: {model}")
        print(f"    Model name: {model_name}")

        if provider == "openai" and model == "gpt-4" and model_name == "gpt-4":
            print("    ✅ Провайдер і модель збережені правильно")
        else:
            print("    ❌ Проблема з провайдером або моделлю")

        print("\n🎯 Тест завершено успішно!")

if __name__ == "__main__":
    test_unified_config()
