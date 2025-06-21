#!/usr/bin/env python3
"""
Тест повного флоу конфігурації:
1. Storage API ключів
2. Перезавантаження конфігурації
3. Verification, що ключі збережені та завантажені правильно
"""

import sys


def test_main_config_manager():
    """Тест основного ConfigManager"""
    print("🔧 Тестування основного ConfigManager...")

    #Імпортуємо основний ConfigManager
    from config_manager import ConfigManager

    config = ConfigManager()

    #Тестові ключі
    test_keys = {
        "openai_api_key": "sk-real-openai-key-12345",
        "gemini_api_key": "AIzaReal-gemini-key-67890",
        "mistral_api_key": "real-mistral-key-abcde",
        "groq_api_key": "gsk_real-groq-key-fghij",
    }

    #Збережемо ключі
    print("  💾 Збереження API ключів...")
    for key, value in test_keys.items():
        config.set_setting(key, value)

    #Перевіримо storage
    print("  🔍 Перевірка збережених ключів...")
    saved_keys = {
        "openai_api_key": config.get_openai_api_key(),
        "gemini_api_key": config.get_gemini_api_key(),
        "mistral_api_key": config.get_mistral_api_key(),
        "groq_api_key": config.get_groq_api_key(),
    }

    for key, expected in test_keys.items():
        actual = saved_keys[key]
        if actual == expected:
            print(f"    ✅ {key}: {actual[:10]}...")
        else:
            print(f"    ❌ {key}: очікувався {expected[:10]}..., отримано {actual[:10]}...")
            return False

    #Створемо new екземпляр для симуляції перезапуску
    print("  🔄 Симуляція перезапуску (новий екземпляр)...")
    config2 = ConfigManager()

    #Перевіримо, що ключі завантажилися
    reloaded_keys = {
        "openai_api_key": config2.get_openai_api_key(),
        "gemini_api_key": config2.get_gemini_api_key(),
        "mistral_api_key": config2.get_mistral_api_key(),
        "groq_api_key": config2.get_groq_api_key(),
    }

    print("  🔍 Перевірка завантажених ключів...")
    for key, expected in test_keys.items():
        actual = reloaded_keys[key]
        if actual == expected:
            print(f"    ✅ {key}: {actual[:10]}...")
        else:
            print(f"    ❌ {key}: очікувався {expected[:10]}..., отримано {actual[:10]}...")
            return False

    return True

def test_utils_config_manager():
    """Тест utils ConfigManager"""
    print("\n🔧 Тестування utils ConfigManager...")

    #Імпортуємо utils ConfigManager
    from utils.config_manager import ConfigManager

    config = ConfigManager()

    #Тестові ключі
    test_keys = {
        "openai_api_key": "sk-utils-openai-key-12345",
        "gemini_api_key": "AIzaUtils-gemini-key-67890",
        "mistral_api_key": "utils-mistral-key-abcde",
        "groq_api_key": "gsk_utils-groq-key-fghij",
    }

    #Збережемо ключі
    print("  💾 Збереження API ключів...")
    for key, value in test_keys.items():
        config.set_setting(key, value)

    #Перевіримо storage
    print("  🔍 Перевірка збережених ключів...")
    saved_keys = {
        "openai_api_key": config.get_openai_api_key(),
        "gemini_api_key": config.get_gemini_api_key(),
        "mistral_api_key": config.get_mistral_api_key(),
        "groq_api_key": config.get_groq_api_key(),
    }

    for key, expected in test_keys.items():
        actual = saved_keys[key]
        if actual == expected:
            print(f"    ✅ {key}: {actual[:10]}...")
        else:
            print(f"    ❌ {key}: очікувався {expected[:10]}..., отримано {actual[:10]}...")
            return False

    return True

def test_llm_manager_integration():
    """Тест інтеграції з LLMManager"""
    print("\n🤖 Тестування інтеграції з LLMManager...")

    try:
        from config_manager import ConfigManager
        from utils.llm_manager import LLMManager

        config = ConfigManager()

        #Встановимо реальні тестові ключі
        config.set_setting("openai_api_key", "sk-test-valid-openai-key-at-least-20-chars")
        config.set_setting("gemini_api_key", "AIzaTest-valid-gemini-key-at-least-20-chars")
        config.set_setting("current_provider", "openai")
        config.set_setting("current_model", "gpt-4")

        #Створемо LLMManager
        llm = LLMManager(config)

        print("  ✅ LLMManager успішно створено")
        print(f"  🔑 Поточний провайдер: {llm.current_provider}")
        print(f"  🤖 Поточна модель: {llm.current_model}")

        return True

    except Exception as e:
        print(f"  ❌ Помилка LLMManager: {e}")
        return False

def main():
    print("🧪 ПОВНИЙ ТЕСТ КОНФІГУРАЦІЙНОГО ФЛОУ")
    print("=" * 50)

    success = True

    #Тест основного ConfigManager
    if not test_main_config_manager():
        success = False

    #Тест utils ConfigManager
    if not test_utils_config_manager():
        success = False

    #Тест інтеграції з LLMManager
    if not test_llm_manager_integration():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 ВСІ ТЕСТИ ПРОЙШЛИ!")
        print("✅ Конфігурація працює правильно")
        print("✅ API ключі зберігаються та завантажуються")
        print("✅ LLMManager інтегрується без помилок")
    else:
        print("❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ")
        print("🔧 Потребують додаткового виправлення")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
