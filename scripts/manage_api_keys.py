#!/usr/bin/env python3
"""
Atlas API Keys Manager
Утиліта для management API ключами в Atlas
"""

import configparser
import getpass
import os
import sys
from pathlib import Path


def manage_api_keys():
    """Інтерактивне management API ключами"""
    print("🔑 Atlas API Keys Manager")
    print("=" * 40)

    # Завантажуємо поточну конфігурацію
    config = configparser.ConfigParser()
    config_path = "config.ini"

    if os.path.exists(config_path):
        config.read(config_path)
        print("✅ Завантажено config.ini")
    else:
        print("❌ config.ini не знайдено")
        return False

    # Показуємо current state
    show_current_keys(config)

    # Пропонуємо опції
    while True:
        print("\n📋 Доступні опції:")
        print("1. Налаштувати OpenAI API ключ")
        print("2. Налаштувати Gemini API ключ")
        print("3. Показати поточний стан")
        print("4. Перевірити API ключі")
        print("5. Вийти")

        choice = input("\n👤 Ваш вибір (1-5): ").strip()

        if choice == "1":
            set_openai_key(config, config_path)
        elif choice == "2":
            set_gemini_key(config, config_path)
        elif choice == "3":
            show_current_keys(config)
        elif choice == "4":
            test_api_keys(config)
        elif choice == "5":
            print("👋 До побачення!")
            break
        else:
            print("❌ Невірний вибір, спробуйте ще раз")


def show_current_keys(config):
    """Показати current state API ключів"""
    print("\n🔍 Поточний стан API ключів:")

    # OpenAI
    if config.has_section("OpenAI") and config.has_option("OpenAI", "api_key"):
        openai_key = config.get("OpenAI", "api_key")
        if (
            openai_key
            and not openai_key.startswith("YOUR_")
            and not openai_key.startswith("sk-your-")
        ):
            print(f"✅ OpenAI: {openai_key[:20]}...")
        else:
            print("⚠️  OpenAI: не налаштовано")
    else:
        print("❌ OpenAI: відсутній")

    # Gemini
    if config.has_section("Gemini") and config.has_option("Gemini", "api_key"):
        gemini_key = config.get("Gemini", "api_key")
        if gemini_key and not gemini_key.startswith("YOUR_"):
            print(f"✅ Gemini: {gemini_key[:20]}...")
        else:
            print("⚠️  Gemini: не налаштовано")
    else:
        print("❌ Gemini: відсутній")


def set_openai_key(config, config_path):
    """Налаштувати OpenAI API ключ"""
    print("\n🔧 Налаштування OpenAI API ключа")
    print("💡 Отримайте ключ на: https://platform.openai.com/account/api-keys")

    # Отримуємо ключ від користувача
    api_key = getpass.getpass("🔑 Введіть OpenAI API ключ (sk-...): ").strip()

    if not api_key:
        print("❌ Ключ не введено")
        return

    if not api_key.startswith("sk-"):
        print("⚠️  OpenAI ключі зазвичай починаються з 'sk-'")
        confirm = input("Продовжити? (y/N): ").strip().lower()
        if confirm != "y":
            return

    # Зберігаємо ключ
    if not config.has_section("OpenAI"):
        config.add_section("OpenAI")

    config.set("OpenAI", "api_key", api_key)
    config.set("OpenAI", "model_name", "gpt-4-turbo")

    save_config(config, config_path)
    print("✅ OpenAI API ключ збережено")


def set_gemini_key(config, config_path):
    """Налаштувати Gemini API ключ"""
    print("\n🔧 Налаштування Gemini API ключа")
    print("💡 Отримайте ключ на: https://makersuite.google.com/app/apikey")

    # Отримуємо ключ від користувача
    api_key = getpass.getpass("🔑 Введіть Gemini API ключ (AIza...): ").strip()

    if not api_key:
        print("❌ Ключ не введено")
        return

    if not api_key.startswith("AIza"):
        print("⚠️  Gemini ключі зазвичай починаються з 'AIza'")
        confirm = input("Продовжити? (y/N): ").strip().lower()
        if confirm != "y":
            return

    # Зберігаємо ключ
    if not config.has_section("Gemini"):
        config.add_section("Gemini")

    config.set("Gemini", "api_key", api_key)
    config.set("Gemini", "model_name", "gemini-1.5-flash")

    save_config(config, config_path)
    print("✅ Gemini API ключ збережено")


def save_config(config, config_path):
    """Зберегти конфігурацію"""
    try:
        with open(config_path, "w") as configfile:
            config.write(configfile)
        print("💾 Конфігурацію збережено")
    except Exception as e:
        print(f"❌ Помилка збереження: {e}")


def test_api_keys(config):
    """Тестувати API ключі"""
    print("\n🧪 Тестування API ключів...")

    # Тест Gemini
    if config.has_section("Gemini") and config.has_option("Gemini", "api_key"):
        gemini_key = config.get("Gemini", "api_key")
        if gemini_key and not gemini_key.startswith("YOUR_"):
            print("🔍 Тестування Gemini API...")
            if test_gemini_api(gemini_key):
                print("✅ Gemini API працює")
            else:
                print("❌ Gemini API не працює")
        else:
            print("⚠️  Gemini API ключ не налаштовано")

    # Тест OpenAI
    if config.has_section("OpenAI") and config.has_option("OpenAI", "api_key"):
        openai_key = config.get("OpenAI", "api_key")
        if (
            openai_key
            and not openai_key.startswith("YOUR_")
            and not openai_key.startswith("sk-your-")
        ):
            print("🔍 Тестування OpenAI API...")
            if test_openai_api(openai_key):
                print("✅ OpenAI API працює")
            else:
                print("❌ OpenAI API не працює")
        else:
            print("⚠️  OpenAI API ключ не налаштовано")


def test_gemini_api(api_key):
    """Тестувати Gemini API"""
    try:
        import google.generativeai as genai

        # Конфігуруємо API
        genai.configure(api_key=api_key)

        # Створюємо модель
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Простий тест
        response = model.generate_content("Скажи привіт українською")

        return bool(response.text)

    except Exception as e:
        print(f"❌ Помилка Gemini API: {e}")
        return False


def test_openai_api(api_key):
    """Тестувати OpenAI API"""
    try:
        import openai

        # Створюємо клієнт
        client = openai.OpenAI(api_key=api_key)

        # Простий тест
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Скажи привіт"}],
            max_tokens=50,
        )

        return bool(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Помилка OpenAI API: {e}")
        return False


def quick_setup():
    """Швидке settings з рекомендаціями"""
    print("🚀 Швидке налаштування API ключів")
    print("=" * 40)

    print("📝 Рекомендації:")
    print("1. Gemini API - безкоштовний і швидкий (рекомендовано)")
    print("2. OpenAI API - платний, але потужний")
    print("3. Gemini налаштовано як основний провайдер")

    print("\n💡 Для нормальної роботи Atlas потрібен принаймні Gemini API ключ")

    # Перевіряємо current state
    config = configparser.ConfigParser()
    if os.path.exists("config.ini"):
        config.read("config.ini")

        # Перевіряємо Gemini
        if config.has_section("Gemini") and config.has_option("Gemini", "api_key"):
            gemini_key = config.get("Gemini", "api_key")
            if gemini_key and not gemini_key.startswith("YOUR_"):
                print("✅ Gemini API вже налаштовано")
                return True

        print("⚠️  Gemini API потребує налаштування")
        setup_gemini = input("Налаштувати зараз? (Y/n): ").strip().lower()
        if setup_gemini != "n":
            set_gemini_key(config, "config.ini")
            return True

    return False


def main():
    """Головна функція"""
    try:
        # Перехід до директорії Atlas
        atlas_dir = Path(__file__).parent
        os.chdir(atlas_dir)

        if len(sys.argv) > 1 and sys.argv[1] == "--quick":
            quick_setup()
        else:
            manage_api_keys()

    except KeyboardInterrupt:
        print("\n\n⚠️  Менеджер API ключів перервано")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
