#!/usr/bin/env python3
"""
Тест GUI з основним ConfigManager
"""

import sys
import tkinter as tk

from ui.enhanced_settings import EnhancedSettingsView
from utils.config_manager import ConfigManager


def test_gui_creation():
    """Тестуємо creation GUI компонента."""
    print("🎨 ТЕСТ СТВОРЕННЯ GUI")
    print("=" * 30)

    #Створюємо ConfigManager
    config_manager = ConfigManager()

    #Встановлюємо тестові API ключі
    print("🔑 Встановлення тестових API ключів...")
    config_manager.set_setting("openai_api_key", "sk-gui-test-openai-key-12345")
    config_manager.set_setting("gemini_api_key", "gem-gui-test-12345")
    config_manager.set_setting("mistral_api_key", "mist-gui-test-12345")
    config_manager.set_setting("groq_api_key", "groq-gui-test-12345")
    config_manager.set_setting("current_provider", "gemini")
    config_manager.set_setting("current_model", "gemini-1.5-flash")

    #Тестуємо всі необхідні методи
    print("📋 Перевірка методів ConfigManager...")
    methods_to_test = [
        "get_setting",
        "set_setting",
        "get_openai_api_key",
        "get_gemini_api_key",
        "get_mistral_api_key",
        "get_groq_api_key",
        "get_current_provider",
        "get_current_model",
        "get_model_name",
        "load",
        "save",
    ]

    for method_name in methods_to_test:
        if hasattr(config_manager, method_name):
            print(f"  ✅ {method_name}: є")
        else:
            print(f"  ❌ {method_name}: відсутній")

    #Тестуємо creation GUI компонента
    print("\n🖥️ Створення GUI компонента...")
    try:
        #Створюємо головне вікно
        root = tk.Tk()
        root.withdraw()  #Ховаємо головне вікно

        #Створюємо тестовий фрейм
        test_frame = tk.Frame(root)

        #Створюємо GUI компонент
        settings_view = EnhancedSettingsView(
            test_frame,
            config_manager=config_manager,
            plugin_manager=None,
            save_callback=None,
        )

        print("  ✅ EnhancedSettingsView створено успішно")

        #Перевіряємо, що settings завантажилися
        if hasattr(settings_view, "settings_vars"):
            print("  ✅ Змінні налаштувань ініціалізовані")
        else:
            print("  ❌ Змінні налаштувань не ініціалізовані")

        #Закриваємо вікно
        root.destroy()

        print("\n🎉 GUI тест пройшов успішно!")
        return True

    except Exception as e:
        print(f"  ❌ Помилка створення GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_creation()
    sys.exit(0 if success else 1)
