#!/usr/bin/env python3
"""
Скрипт для виправлення проблем з API ключами в Atlas
"""

import os
import shutil
import yaml
from pathlib import Path

def clear_atlas_data():
    """Очистити всі data Atlas"""
    print("🧹 Очищення даних Atlas...")
    
    #Можливі шляхи до конфігурації
    atlas_paths = [
        Path.home() / ".atlas",
        Path("/Users/dev/.atlas"),
        Path("~/.atlas").expanduser(),
        Path(".atlas"),
    ]
    
    for path in atlas_paths:
        if path.exists():
            print(f"  🗑️  Видалення {path}")
            shutil.rmtree(path, ignore_errors=True)
    
    #Видалити векторну базу
    chroma_paths = [
        Path("chroma.db"),
        Path("memory"),
        Path("*.db"),
    ]
    
    for pattern in ["chroma*", "*.db", "memory"]:
        import glob
        for file in glob.glob(pattern):
            print(f"  🗑️  Видалення {file}")
            if os.path.isdir(file):
                shutil.rmtree(file, ignore_errors=True)
            else:
                os.remove(file)

def create_clean_config():
    """Створити чисту конфігурацію"""
    print("📝 Створення чистої конфігурації...")
    
    config_dir = Path.home() / ".atlas"
    config_dir.mkdir(exist_ok=True)
    
    config = {
        "api_keys": {
            "openai": "",
            "gemini": "",
            "groq": "",
            "mistral": "",
            "anthropic": ""
        },
        "current_provider": "gemini",
        "current_model": "gemini-1.5-flash",
        "agents": {
            "Browser Agent": {"provider": "gemini", "model": "gemini-1.5-flash"},
            "Screen Agent": {"provider": "gemini", "model": "gemini-1.5-flash"},
            "Text Agent": {"provider": "gemini", "model": "gemini-1.5-flash"},
            "System Interaction Agent": {"provider": "gemini", "model": "gemini-1.5-flash"},
        },
        "security": {
            "destructive_op_threshold": 80,
            "api_usage_threshold": 50,
            "file_access_threshold": 70,
            "rules": []
        }
    }
    
    config_file = config_dir / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"✅ Конфігурація створена: {config_file}")

def check_env_variables():
    """Перевірити змінні середовища та .env файл"""
    print("🔍 Перевірка змінних середовища та .env файлу...")
    
    env_vars = [
        "OPENAI_API_KEY",
        "GEMINI_API_KEY", 
        "GROQ_API_KEY",
        "MISTRAL_API_KEY"
    ]
    
    #Перевірити .env файл
    env_file = Path(".env")
    if env_file.exists():
        print(f"  ✅ Знайдено .env файл: {env_file.absolute()}")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("  ❌ .env файл не знайдено")
    
    found_keys = []
    for var in env_vars:
        value = os.getenv(var)
        if value and value != "your_real_gemini_key_here" and value != "your_real_mistral_key_here" and value != "your_real_groq_key_here":
            print(f"  ✅ {var}: {'*' * max(1, len(value) - 8)}{value[-8:] if len(value) > 8 else value[-4:]}")
            found_keys.append(var)
        else:
            print(f"  ❌ {var}: не знайдено або є тестовим значенням")
    
    return found_keys

def main():
    print("🔧 Atlas API Keys Fix Script")
    print("=" * 50)
    
    #1. Очистити старі data
    clear_atlas_data()
    
    #2. Створити чисту конфігурацію  
    create_clean_config()
    
    #3. Перевірити змінні середовища
    found_keys = check_env_variables()
    
    print("\n" + "=" * 50)
    print("🎯 РЕЗУЛЬТАТ:")
    
    if found_keys:
        print(f"✅ Знайдено API ключі: {', '.join(found_keys)}")
        print("📝 Atlas буде використовувати ключі з .env файлу")
    else:
        print("❌ API ключі не знайдено або мають тестові значення")
        print("📝 Встановіть справжні ключі:")
        print("   1. Відредагуйте .env файл у корені проекту")
        print("   2. Або встановіть через GUI Atlas (вкладка Settings)")
        print("   3. Або через змінні середовища:")
        print("      export GEMINI_API_KEY='your_real_key_here'")
        print("      export MISTRAL_API_KEY='your_real_key_here'")
    
    print(f"\n💡 Пріоритет ключів: .env файл → змінні середовища → GUI конфігурація")
    print("🚀 Тепер перезапустіть Atlas!")

if __name__ == "__main__":
    main()
