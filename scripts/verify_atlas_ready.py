#!/usr/bin/env python3
"""
Atlas Final Verification Script
Фінальна verification всіх виправлень та готовності Atlas
"""

import configparser
import os
import sys
from pathlib import Path


def final_verification():
    """Фінальна verification готовності Atlas"""
    print("🎯 Atlas Final Verification")
    print("=" * 40)

    checks = [
        ("📁 Файли конфігурації", check_config_files),
        ("🔑 API ключі", check_api_keys),
        ("🐍 Python середовище", check_python_env),
        ("📦 Залежності", check_dependencies),
        ("⚙️  ConfigManager методи", check_config_manager_methods),
        ("🤖 LLMManager атрибути", check_llm_manager_attributes),
        ("💾 Збереження налаштувань", check_settings_save),
    ]

    passed = 0
    total = len(checks)

    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            if check_func():
                print("✅ ПРОЙДЕНО")
                passed += 1
            else:
                print("❌ ПРОВАЛЕНО")
        except Exception as e:
            print(f"❌ ПОМИЛКА: {e}")

    print("\n" + "=" * 40)
    print(f"📊 Результат: {passed}/{total} перевірок пройдено")

    if passed == total:
        print("🎉 Atlas повністю готовий до роботи!")
        print("\n🚀 Способи запуску:")
        print("   1. ./launch_atlas.sh         (рекомендовано)")
        print("   2. python3 main.py          (базовий)")
        print("   3. ./launch_macos.sh        (якщо є)")

        print("\n🔧 Додаткові утиліти:")
        print("   • python3 diagnose_atlas.py    - діагностика")
        print("   • python3 setup_atlas_quick.py - швидке налаштування")

        return True
    print("⚠️  Є проблеми, які потребують уваги")
    print("\n🔧 Для виправлення:")
    print("   python3 setup_atlas_quick.py")

    return False

def check_config_files():
    """Verification файлів конфігурації"""
    required_files = ["config.ini", ".env"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"  ❌ {file} відсутній")
            return False
        print(f"  ✅ {file}")

    #Verification YAML
    yaml_path = Path.home() / ".atlas" / "config.yaml"
    if yaml_path.exists():
        print("  ✅ ~/.atlas/config.yaml")
    else:
        print("  ⚠️  ~/.atlas/config.yaml відсутній")

    return True

def check_api_keys():
    """Verification API ключів"""
    if not os.path.exists("config.ini"):
        return False

    config = configparser.ConfigParser()
    config.read("config.ini")

    #Gemini ключ
    if config.has_section("Gemini") and config.has_option("Gemini", "api_key"):
        key = config.get("Gemini", "api_key")
        if key and not key.startswith("YOUR_"):
            print("  ✅ Gemini API ключ")
        else:
            print("  ❌ Gemini API ключ не налаштовано")
            return False
    else:
        print("  ❌ Gemini API ключ відсутній")
        return False

    return True

def check_python_env():
    """Verification Python середовища"""
    #Версія Python
    if sys.version_info < (3, 8):
        print(f"  ❌ Python {sys.version_info.major}.{sys.version_info.minor} занадто старий")
        return False
    print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    #Віртуальне середовище
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        print("  ✅ Віртуальне середовище активне")
        if "venv-macos" in sys.prefix:
            print("  ✅ Використовується venv-macos")
    else:
        print("  ⚠️  Віртуальне середовище не активне")

    return True

def check_dependencies():
    """Verification залежностей"""
    critical_deps = [
        ("google.generativeai", "google-generativeai"),
        ("openai", "openai"),
        ("customtkinter", "customtkinter"),
        ("chromadb", "chromadb"),
    ]

    for module, package in critical_deps:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} не встановлено")
            return False

    return True

def check_config_manager_methods():
    """Verification методів ConfigManager"""
    try:
        #Основний ConfigManager
        from config_manager import ConfigManager
        config_mgr = ConfigManager()

        required_methods = ["set_llm_provider_and_model", "set_llm_api_key"]
        for method in required_methods:
            if hasattr(config_mgr, method):
                print(f"  ✅ ConfigManager.{method}")
            else:
                print(f"  ❌ ConfigManager.{method} відсутній")
                return False

        #Utils ConfigManager
        from utils.config_manager import ConfigManager as UtilsConfigManager
        utils_config_mgr = UtilsConfigManager()

        for method in required_methods:
            if hasattr(utils_config_mgr, method):
                print(f"  ✅ utils.ConfigManager.{method}")
            else:
                print(f"  ❌ utils.ConfigManager.{method} відсутній")
                return False

        return True

    except Exception as e:
        print(f"  ❌ Помилка імпорту: {e}")
        return False

def check_llm_manager_attributes():
    """Verification атрибутів LLMManager"""
    try:
        #Mock TokenTracker
        class MockTokenTracker:
            def add_usage(self, usage):
                pass

        from utils.llm_manager import LLMManager

        token_tracker = MockTokenTracker()
        llm_mgr = LLMManager(token_tracker)

        required_attrs = ["gemini_model", "openai_model"]
        for attr in required_attrs:
            if hasattr(llm_mgr, attr):
                print(f"  ✅ LLMManager.{attr}")
            else:
                print(f"  ❌ LLMManager.{attr} відсутній")
                return False

        return True

    except Exception as e:
        print(f"  ❌ Помилка ініціалізації LLMManager: {e}")
        return False

def check_settings_save():
    """Verification storage налаштувань"""
    try:
        #Тестуємо основний ConfigManager
        from config_manager import ConfigManager
        config_mgr = ConfigManager()

        #Тестове storage
        test_result = config_mgr.set_llm_provider_and_model("gemini", "gemini-1.5-flash")
        if test_result:
            print("  ✅ Збереження провайдера/моделі працює")
        else:
            print("  ❌ Збереження провайдера/моделі не працює")
            return False

        #Тестуємо storage API ключа
        test_key_result = config_mgr.set_llm_api_key("test_provider", "test_key")
        if test_key_result:
            print("  ✅ Збереження API ключа працює")
        else:
            print("  ❌ Збереження API ключа не працює")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Помилка тестування збереження: {e}")
        return False

def main():
    """Головна функція"""
    try:
        #Перехід до директорії Atlas
        atlas_dir = Path(__file__).parent
        os.chdir(atlas_dir)

        success = final_verification()

        if success:
            print("\n🎊 Вітаємо! Atlas готовий до роботи!")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Перевірка перервана користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Помилка перевірки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
