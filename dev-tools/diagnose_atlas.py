#!/usr/bin/env python3
"""
Atlas Configuration Diagnostics
Діагностика конфігурації Atlas для виявлення проблем
"""

import configparser
import json
import os
import sys
from pathlib import Path


def diagnose_configuration():
    """Повна діагностика конфігурації Atlas"""
    print("🔍 Atlas Configuration Diagnostics")
    print("=" * 50)

    issues = []
    warnings = []

    #1. Verification файлів конфігурації
    config_files = check_config_files()
    if config_files["issues"]:
        issues.extend(config_files["issues"])
    if config_files["warnings"]:
        warnings.extend(config_files["warnings"])

    #2. Verification API ключів
    api_keys = check_api_keys()
    if api_keys["issues"]:
        issues.extend(api_keys["issues"])
    if api_keys["warnings"]:
        warnings.extend(api_keys["warnings"])

    #3. Verification Python середовища
    python_env = check_python_environment()
    if python_env["issues"]:
        issues.extend(python_env["issues"])
    if python_env["warnings"]:
        warnings.extend(python_env["warnings"])

    #4. Verification залежностей
    dependencies = check_dependencies()
    if dependencies["issues"]:
        issues.extend(dependencies["issues"])
    if dependencies["warnings"]:
        warnings.extend(dependencies["warnings"])

    #5. Показати результати
    show_diagnostic_results(issues, warnings)

    return len(issues) == 0

def check_config_files():
    """Verification файлів конфігурації"""
    print("\n📁 Перевірка файлів конфігурації...")

    issues = []
    warnings = []

    #config.ini
    if not os.path.exists("config.ini"):
        issues.append("config.ini не знайдено")
    else:
        print("✅ config.ini знайдено")

        #Verification структури config.ini
        config = configparser.ConfigParser()
        try:
            config.read("config.ini")

            required_sections = ["LLM", "Gemini"]
            for section in required_sections:
                if not config.has_section(section):
                    issues.append(f"Відсутня секція [{section}] в config.ini")
                else:
                    print(f"✅ Секція [{section}] знайдена")
        except Exception as e:
            issues.append(f"Помилка читання config.ini: {e}")

    #.env файл
    if not os.path.exists(".env"):
        warnings.append(".env файл не знайдено")
    else:
        print("✅ .env файл знайдено")

    #YAML configuration
    yaml_path = Path.home() / ".atlas" / "config.yaml"
    if not yaml_path.exists():
        warnings.append("YAML конфігурація не знайдена")
    else:
        print("✅ YAML конфігурація знайдена")

    return {"issues": issues, "warnings": warnings}

def check_api_keys():
    """Verification API ключів"""
    print("\n🔑 Перевірка API ключів...")

    issues = []
    warnings = []

    #Verification в config.ini
    if os.path.exists("config.ini"):
        config = configparser.ConfigParser()
        config.read("config.ini")

        #Gemini API ключ
        if config.has_section("Gemini") and config.has_option("Gemini", "api_key"):
            gemini_key = config.get("Gemini", "api_key")
            if gemini_key and not gemini_key.startswith("YOUR_"):
                print("✅ Gemini API ключ налаштовано")
            else:
                issues.append("Gemini API ключ не налаштовано в config.ini")
        else:
            issues.append("Gemini API ключ відсутній в config.ini")

        #OpenAI API ключ
        if config.has_section("OpenAI") and config.has_option("OpenAI", "api_key"):
            openai_key = config.get("OpenAI", "api_key")
            if openai_key and not openai_key.startswith("sk-your-"):
                print("✅ OpenAI API ключ налаштовано")
            else:
                warnings.append("OpenAI API ключ не налаштовано")

    #Verification в .env
    if os.path.exists(".env"):
        with open(".env") as f:
            env_content = f.read()

        if "GEMINI_API_KEY=" in env_content:
            for line in env_content.split("\n"):
                if line.startswith("GEMINI_API_KEY="):
                    key_value = line.split("=", 1)[1]
                    if key_value and not key_value.startswith("your-"):
                        print("✅ Gemini API ключ знайдено в .env")
                    else:
                        warnings.append("Gemini API ключ в .env не налаштовано")
                    break

    return {"issues": issues, "warnings": warnings}

def check_python_environment():
    """Verification Python середовища"""
    print("\n🐍 Перевірка Python середовища...")

    issues = []
    warnings = []

    #Версія Python
    python_version = sys.version_info
    print(f"✅ Python версія: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 8):
        issues.append(f"Python версія {python_version.major}.{python_version.minor} занадто стара. Потрібно 3.8+")
    elif python_version >= (3, 13):
        print("✅ Python версія оптимальна для macOS")

    #Віртуальне середовище
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        print("✅ Активовано віртуальне середовище")

        #Verification venv-macos
        if "venv-macos" in sys.prefix:
            print("✅ Використовується venv-macos")
        else:
            warnings.append("Рекомендується використовувати venv-macos")
    else:
        warnings.append("Віртуальне середовище не активовано")

    return {"issues": issues, "warnings": warnings}

def check_dependencies():
    """Verification залежностей"""
    print("\n📦 Перевірка залежностей...")

    issues = []
    warnings = []

    critical_packages = [
        "google-generativeai",
        "openai",
        "customtkinter",
        "chromadb",
    ]

    optional_packages = [
        "pyautogui",
        "Pillow",
        "requests",
    ]

    #Verification критичних пакетів
    for package in critical_packages:
        try:
            __import__(package.replace("-", "_").replace("google_generativeai", "google.generativeai"))
            print(f"✅ {package}")
        except ImportError:
            issues.append(f"Критичний пакет {package} не встановлено")

    #Verification опціональних пакетів
    for package in optional_packages:
        try:
            __import__(package.lower())
            print(f"✅ {package}")
        except ImportError:
            warnings.append(f"Опціональний пакет {package} не встановлено")

    return {"issues": issues, "warnings": warnings}

def show_diagnostic_results(issues, warnings):
    """Показати результати діагностики"""
    print("\n" + "=" * 50)
    print("📊 Результати діагностики:")
    print("=" * 50)

    if not issues and not warnings:
        print("🎉 Конфігурація Atlas в ідеальному стані!")
        print("🚀 Можете запускати: python3 main.py")
        return

    if issues:
        print(f"\n❌ Критичні проблеми ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")

    if warnings:
        print(f"\n⚠️  Попередження ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")

    #Рекомендації по виправленню
    print("\n🔧 Рекомендації:")

    if issues:
        print("Для виправлення критичних проблем:")
        print("   1. Запустіть: python3 setup_atlas_quick.py")
        print("   2. Перевірте API ключі в .env та config.ini")
        print("   3. Встановіть відсутні залежності: pip install -r requirements-macos.txt")

    if warnings:
        print("Для усунення попереджень:")
        print("   1. Активуйте venv-macos: source venv-macos/bin/activate")
        print("   2. Налаштуйте додаткові API ключі")
        print("   3. Встановіть опціональні пакети")

def generate_diagnostic_report():
    """Генерувати детальний звіт діагностики"""
    print("\n📋 Генерація детального звіту...")

    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "files": {},
        "environment": {},
    }

    #Інформація про файли
    files_to_check = ["config.ini", ".env", "main.py", "requirements-macos.txt"]
    for file in files_to_check:
        report["files"][file] = {
            "exists": os.path.exists(file),
            "size": os.path.getsize(file) if os.path.exists(file) else 0,
        }

    #Змінні середовища
    env_vars = ["GEMINI_API_KEY", "OPENAI_API_KEY", "PATH", "PYTHONPATH"]
    for var in env_vars:
        value = os.getenv(var, "")
        #Приховуємо API ключі
        if "API_KEY" in var and value:
            value = value[:10] + "..." if len(value) > 10 else "***"
        report["environment"][var] = value

    #Зберігаємо звіт
    report_path = "atlas_diagnostic_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Звіт збережено: {report_path}")

def main():
    """Головна функція"""
    try:
        #Перехід до директорії Atlas
        atlas_dir = Path(__file__).parent
        os.chdir(atlas_dir)

        success = diagnose_configuration()

        #Генеруємо звіт
        generate_diagnostic_report()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Діагностика перервана користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Помилка діагностики: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
