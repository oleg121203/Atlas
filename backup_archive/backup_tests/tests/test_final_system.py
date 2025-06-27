#!/usr/bin/env python3
"""
Фінальний тест всієї системи конфігурації Atlas
"""

import sys
import tempfile
from pathlib import Path

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


def test_complete_system():
    """Тестуємо повну систему конфігурації."""
    print("🎯 ФІНАЛЬНИЙ ТЕСТ СИСТЕМИ ATLAS")
    print("=" * 50)

    # Створюємо тимчасовий ConfigManager
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        config_manager = ConfigManager(config_path)

        print("🔑 Тестування API ключів...")

        # Встановлюємо правильні API ключі (довші за 10 символів)
        api_keys = {
            "openai_api_key": "sk-1234567890abcdef1234567890abcdef12345678",
            "gemini_api_key": "AIzaSy1234567890abcdef1234567890abcdef12",
            "mistral_api_key": "mst_1234567890abcdef1234567890abcdef123456",
            "groq_api_key": "gsk_1234567890abcdef1234567890abcdef123456",
        }

        # Зберігаємо через ConfigManager
        print("  💾 Збереження через ConfigManager...")
        for key, value in api_keys.items():
            config_manager.set_setting(key, value)

        # Встановлюємо провайдер та модель
        config_manager.set_setting("current_provider", "gemini")
        config_manager.set_setting("current_model", "gemini-1.5-flash")

        print("  📖 Перевірка збереження...")
        all_good = True
        for key, expected_value in api_keys.items():
            actual_value = config_manager.get_setting(key)
            if actual_value == expected_value:
                print(f"    ✅ {key}: збережено правильно")
            else:
                print(
                    f"    ❌ {key}: очікували '{expected_value}', отримали '{actual_value}'"
                )
                all_good = False

        # Тестуємо LLMManager з правильними ключами
        print("\n🤖 Тестування LLMManager...")
        try:
            from modules.agents.token_tracker import TokenTracker

            token_tracker = TokenTracker()
            llm_manager = LLMManager(
                token_tracker=token_tracker, config_manager=config_manager
            )
            print("    ✅ LLMManager створено успішно")

            # Тестуємо провайдери
            available_providers = llm_manager.get_available_providers()
            print(f"    📋 Доступні провайдери: {available_providers}")

        except Exception as e:
            print(f"    ❌ Помилка в LLMManager: {e}")
            all_good = False

        # Тестуємо loading після перезапуску
        print("\n🔄 Тестування перезавантаження...")
        new_config_manager = ConfigManager(config_path)

        for key, expected_value in api_keys.items():
            actual_value = new_config_manager.get_setting(key)
            if actual_value == expected_value:
                print(f"    ✅ {key}: завантажено після перезапуску")
            else:
                print(f"    ❌ {key}: втрачено після перезапуску")
                all_good = False

        # Фінальна verification
        print("\n" + "=" * 50)
        if all_good:
            print("🎉 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
            print("✅ Система конфігурації Atlas працює правильно")
        else:
            print("❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ")
            print("🔧 Потрібне додаткове налаштування")

        return all_good


if __name__ == "__main__":
    success = test_complete_system()
    sys.exit(0 if success else 1)
