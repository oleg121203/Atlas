#!/usr/bin/env python3
"""
Швидкий тест API ключів та провайдерів
"""
import os
import sys
from pathlib import Path

#Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🔧 Тест API ключів та налаштувань")
    print("=" * 40)
    
    #Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    from config_manager import ConfigManager
    config = ConfigManager()
    
    print("\n📋 API ключі:")
    print(f"   OpenAI: {'✓' if config.get_openai_api_key() else '✗'}")
    print(f"   Gemini: {'✓' if config.get_gemini_api_key() else '✗'}")
    print(f"   Mistral: {'✓' if config.get_mistral_api_key() else '✗'}")
    print(f"   Groq: {'✓' if config.get_groq_api_key() else '✗'}")
    
    print("\n⚙️ Налаштування:")
    print(f"   Провайдер: {config.get_current_provider()}")
    print(f"   Модель: {config.get_current_model()}")
    
    print("\n🔍 .env файл:")
    env_vars = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'MISTRAL_API_KEY', 'GROQ_API_KEY', 'DEFAULT_LLM_PROVIDER', 'DEFAULT_LLM_MODEL']
    for var in env_vars:
        value = os.getenv(var, '')
        if var.endswith('_KEY'):
            display_value = '✓' if value else '✗'
        else:
            display_value = value if value else '✗'
        print(f"   {var}: {display_value}")

if __name__ == "__main__":
    main()
