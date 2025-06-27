#!/usr/bin/env python3
"""
Швидке очищення тестових API ключів з конфігурації Atlas
"""

import sys

sys.path.append("/workspaces/autoclicker")


def clean_test_keys():
    """Очистити всі тестові ключі з конфігурації"""
    try:
        from config_manager import ConfigManager

        config = ConfigManager()
        settings = config.load()

        print("🧹 Очищення тестових API ключів...")

        if "api_keys" not in settings:
            settings["api_keys"] = {}

        # Тестові ключі для deletion
        test_keys = [
            "111",
            "test",
            "demo",
            "example",
            "test_openai_key",
            "test_gemini_key",
            "test_mistral_key",
        ]

        cleaned = []
        for provider in ["openai", "gemini", "mistral", "groq", "anthropic"]:
            current_key = settings["api_keys"].get(provider, "")

            if current_key in test_keys or len(current_key) < 10:
                if current_key:
                    print(f"🗑️  Видалено тестовий ключ {provider}: [{current_key}]")
                    cleaned.append(provider)
                settings["api_keys"][provider] = ""
            else:
                print(f"✅ {provider}: {'Встановлено' if current_key else 'Порожньо'}")

        # Зберегти конфігурацію
        config.save(settings)

        if cleaned:
            print(f"\n🎯 Очищено тестові ключі: {', '.join(cleaned)}")
        else:
            print("\n✨ Тестових ключів не знайдено")

        print("\n📝 Рекомендації:")
        print("1. Встановіть справжні API ключі через GUI Atlas")
        print("2. Або експортуйте змінні середовища:")
        print("   export GEMINI_API_KEY='your_real_key'")
        print("   export MISTRAL_API_KEY='your_real_key'")

        return True

    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Atlas - Очищення тестових API ключів")
    print("=" * 50)

    success = clean_test_keys()

    print("\n" + "=" * 50)
    if success:
        print("✅ ОЧИЩЕННЯ ЗАВЕРШЕНО")
        print("🚀 Перезапустіть Atlas для застосування змін")
    else:
        print("❌ Виникли помилки під час очищення")
