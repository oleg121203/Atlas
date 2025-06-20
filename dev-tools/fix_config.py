#!/usr/bin/env python3
"""
Script to fix Atlas configuration issues.
Створює config.ini та налаштовує правильні значення за замовчуванням.
"""

import os
import shutil
import configparser
from pathlib import Path

def create_config_from_example():
    """Create config.ini from example if it doesn't exist"""
    config_path = "config.ini"
    example_path = "dev-tools/setup/config.ini.example"
    
    if not os.path.exists(config_path):
        if os.path.exists(example_path):
            shutil.copy(example_path, config_path)
            print(f"✅ Created {config_path} from {example_path}")
        else:
            print(f"⚠️  {example_path} not found, creating default config.ini")
            create_default_config()
        return True
    else:
        print(f"✅ {config_path} already exists")
        return True

def create_default_config():
    """Create a default config.ini file"""
    config = configparser.ConfigParser()
    
    config['OpenAI'] = {
        'API_KEY': 'YOUR_OPENAI_API_KEY_HERE',
        'MODEL_NAME': 'gpt-4-turbo'
    }
    
    config['Gemini'] = {
        'API_KEY': 'YOUR_GEMINI_API_KEY_HERE',
        'MODEL_NAME': 'gemini-1.5-flash'
    }
    
    config['LLM'] = {
        'provider': 'gemini',
        'model': 'gemini-1.5-flash'
    }
    
    config['App'] = {
        'DEFAULT_GOAL': 'Analyze the current screen and suggest the next action.'
    }
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("✅ Created default config.ini")

def update_config_with_gemini_defaults():
    """Update existing config.ini to include Gemini defaults"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    #Add Gemini section if missing
    if not config.has_section('Gemini'):
        config.add_section('Gemini')
        config.set('Gemini', 'API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
        config.set('Gemini', 'MODEL_NAME', 'gemini-1.5-flash')
        print("✅ Added Gemini section to config.ini")
    
    #Add LLM section if missing
    if not config.has_section('LLM'):
        config.add_section('LLM')
        config.set('LLM', 'provider', 'gemini')
        config.set('LLM', 'model', 'gemini-1.5-flash')
        print("✅ Added LLM section to config.ini")
    
    #Save updated config
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    print("✅ Updated config.ini with Gemini defaults")

def main():
    """Main function to fix configuration"""
    print("🔧 Fixing Atlas Configuration Issues...")
    print("=" * 40)
    
    #Change to Atlas directory
    atlas_dir = Path(__file__).parent
    os.chdir(atlas_dir)
    
    #Create or update config.ini
    create_config_from_example()
    update_config_with_gemini_defaults()
    
    print("\n📝 Next steps:")
    print("1. Edit config.ini with your actual API keys:")
    print("   - Add your Gemini API key to [Gemini] section")
    print("   - Optionally add OpenAI API key to [OpenAI] section")
    print("2. Restart Atlas: python3 main.py")
    print("\n🚀 Configuration fix completed!")

if __name__ == "__main__":
    main()
