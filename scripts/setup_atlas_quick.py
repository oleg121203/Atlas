#!/usr/bin/env python3
"""
Atlas Quick Setup Utility
Швидке settings Atlas для macOS з автоматичною конфігурацією
"""

import configparser
import os
import shutil
import sys
from pathlib import Path


def setup_atlas_config():
    """Автоматичне settings Atlas конфігурації"""
    print("🍎 Atlas macOS Quick Setup")
    print("=" * 40)

    # 1. Перевіряємо config.ini
    if not os.path.exists("config.ini"):
        print("📝 Створення config.ini...")

        # Копіюємо з прикладу або створюємо new
        if os.path.exists("dev-tools/setup/config.ini.example"):
            shutil.copy("dev-tools/setup/config.ini.example", "config.ini")
            print("✅ Скопійовано з прикладу")
        else:
            create_default_config()
            print("✅ Створено за замовчуванням")
    else:
        print("✅ config.ini вже існує")

    # 2. Перевіряємо API ключі в .env
    setup_api_keys()

    # 3. Налаштовуємо config.ini з правильними значеннями
    update_config_ini()

    # 4. Перевіряємо YAML конфігурацію
    setup_yaml_config()

    # 5. Показуємо фінальний status
    show_setup_status()


def create_default_config():
    """Створити config.ini за замовчуванням"""
    config = configparser.ConfigParser()

    config["OpenAI"] = {
        "api_key": "sk-your-openai-api-key-here",
        "model_name": "gpt-4-turbo",
    }

    config["Gemini"] = {
        "api_key": "YOUR_GEMINI_API_KEY_HERE",
        "model_name": "gemini-1.5-flash",
    }

    config["LLM"] = {
        "provider": "gemini",
        "model": "gemini-1.5-flash",
    }

    config["UI"] = {
        "theme": "dark",
        "language": "en",
    }

    config["Security"] = {
        "enable_sandbox": "true",
        "max_file_size": "10485760",
    }

    config["Performance"] = {
        "max_workers": "4",
        "timeout": "30",
    }

    with open("config.ini", "w") as configfile:
        config.write(configfile)


def setup_api_keys():
    """Settings API ключів з .env файлу"""
    print("\n🔑 Перевірка API ключів...")

    if os.path.exists(".env"):
        with open(".env") as f:
            env_content = f.read()

        # Перевіряємо наявність ключів
        keys_found = {}
        for provider in ["OPENAI", "GEMINI", "GROQ", "MISTRAL"]:
            key_pattern = f"{provider}_API_KEY="
            if key_pattern in env_content:
                # Витягуємо значення ключа
                for line in env_content.split("\n"):
                    if line.startswith(key_pattern):
                        key_value = line.split("=", 1)[1]
                        if (
                            key_value
                            and not key_value.startswith("your-")
                            and not key_value.startswith("sk-your-")
                        ):
                            keys_found[provider] = key_value
                            print(f"✅ {provider} API ключ знайдено")
                        else:
                            print(f"⚠️  {provider} API ключ не налаштовано")

        return keys_found
    print("⚠️  .env файл не знайдено")
    return {}


def update_config_ini():
    """Оновити config.ini з правильними значеннями"""
    print("\n📝 Оновлення config.ini...")

    config = configparser.ConfigParser()
    config.read("config.ini")

    # Читаємо ключі з .env
    env_keys = {}
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_keys[key] = value

    # Оновлюємо конфігурацію
    updates_made = False

    # Gemini API ключ
    if env_keys.get("GEMINI_API_KEY"):
        if not config.has_section("Gemini"):
            config.add_section("Gemini")
        config.set("Gemini", "api_key", env_keys["GEMINI_API_KEY"])
        updates_made = True
        print("✅ Gemini API ключ оновлено")

    # OpenAI API ключ
    if env_keys.get("OPENAI_API_KEY"):
        if not config.has_section("OpenAI"):
            config.add_section("OpenAI")
        config.set("OpenAI", "api_key", env_keys["OPENAI_API_KEY"])
        updates_made = True
        print("✅ OpenAI API ключ оновлено")

    # LLM settings
    if not config.has_section("LLM"):
        config.add_section("LLM")
        config.set("LLM", "provider", "gemini")
        config.set("LLM", "model", "gemini-1.5-flash")
        updates_made = True
        print("✅ LLM налаштування додано")

    # Зберігаємо зміни
    if updates_made:
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        print("✅ config.ini оновлено")


def setup_yaml_config():
    """Settings YAML конфігурації"""
    print("\n🔧 Перевірка YAML конфігурації...")

    yaml_path = Path.home() / ".atlas" / "config.yaml"
    yaml_path.parent.mkdir(exist_ok=True)

    if not yaml_path.exists():
        # Створюємо базову YAML конфігурацію
        yaml_content = """current_provider: gemini
current_model: gemini-1.5-flash
agents:
  Browser Agent:
    provider: gemini
    model: gemini-1.5-flash
    fallback_chain: []
  Screen Agent:
    provider: gemini
    model: gemini-1.5-flash
    fallback_chain: []
  Text Agent:
    provider: gemini
    model: gemini-1.5-flash
    fallback_chain: []
  System Interaction Agent:
    provider: gemini
    model: gemini-1.5-flash
    fallback_chain: []
security:
  destructive_op_threshold: 80
  api_usage_threshold: 50
  file_access_threshold: 70
  rules:
    - "#Example Rule: Deny all shell commands that contain 'rm -rf'"
    - "DENY,TERMINAL,.*rm -rf.*"
"""

        with open(yaml_path, "w") as f:
            f.write(yaml_content)
        print("✅ YAML конфігурація створена")
    else:
        print("✅ YAML конфігурація вже існує")


def show_setup_status():
    """Показати фінальний status settings"""
    print("\n" + "=" * 40)
    print("📊 Статус налаштування Atlas:")
    print("=" * 40)

    # Перевіряємо файли
    files_status = {
        "config.ini": os.path.exists("config.ini"),
        ".env": os.path.exists(".env"),
        "~/.atlas/config.yaml": (Path.home() / ".atlas" / "config.yaml").exists(),
    }

    for file, exists in files_status.items():
        status = "✅" if exists else "❌"
        print(f"{status} {file}")

    # Перевіряємо API ключі
    print("\n🔑 API ключі:")
    if os.path.exists("config.ini"):
        config = configparser.ConfigParser()
        config.read("config.ini")

        for section in ["Gemini", "OpenAI"]:
            if config.has_section(section) and config.has_option(section, "api_key"):
                key = config.get(section, "api_key")
                if (
                    key
                    and not key.startswith("YOUR_")
                    and not key.startswith("sk-your-")
                ):
                    print(f"✅ {section} API ключ налаштовано")
                else:
                    print(f"⚠️  {section} API ключ потребує налаштування")

    print("\n🚀 Для запуску Atlas:")
    print("   python3 main.py")

    print("\n🔧 Для тестування:")
    print("   ./quick_test_macos.sh")


def main():
    """Головна функція"""
    try:
        # Перехід до директорії Atlas
        atlas_dir = Path(__file__).parent
        os.chdir(atlas_dir)

        setup_atlas_config()

    except KeyboardInterrupt:
        print("\n\n⚠️  Налаштування перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Помилка налаштування: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
