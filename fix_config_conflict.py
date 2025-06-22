#!/usr/bin/env python3
"""
Fix configuration conflict between .env, config.ini, and config.yaml
"""

import os
from pathlib import Path
from utils.config_manager import ConfigManager

def check_config_conflicts():
    """Check for configuration conflicts."""
    print("🔍 Checking Configuration Conflicts")
    print("=" * 50)
    
    conflicts = []
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("📄 .env file found")
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        # Check for placeholder keys
        if "your-groq-key-here" in env_content:
            conflicts.append("❌ .env contains placeholder Groq key")
        if "your-mistral-key-here" in env_content:
            conflicts.append("❌ .env contains placeholder Mistral key")
            
        # Check for hardcoded provider
        if "DEFAULT_LLM_PROVIDER=gemini" in env_content:
            conflicts.append("⚠️ .env forces Gemini as default provider")
            
    else:
        print("📄 .env file not found")
    
    # Check config.ini
    ini_file = Path("config.ini")
    if ini_file.exists():
        print("📄 config.ini found")
        with open(ini_file, 'r') as f:
            ini_content = f.read()
            
        if "provider = gemini" in ini_content:
            conflicts.append("⚠️ config.ini forces Gemini as provider")
    else:
        print("📄 config.ini not found")
    
    # Check config.yaml
    yaml_file = Path.home() / ".atlas" / "config.yaml"
    if yaml_file.exists():
        print("📄 ~/.atlas/config.yaml found")
        config_manager = ConfigManager()
        config = config_manager.load()
        
        current_provider = config.get("current_provider", "N/A")
        api_keys = config.get("api_keys", {})
        
        print(f"   Current provider: {current_provider}")
        print(f"   API keys configured: {list(api_keys.keys())}")
        
        if current_provider == "gemini":
            conflicts.append("⚠️ config.yaml uses Gemini as provider")
            
        # Check for empty API keys
        for provider, key in api_keys.items():
            if not key or key == "":
                conflicts.append(f"⚠️ {provider} API key is empty in config.yaml")
    else:
        print("📄 ~/.atlas/config.yaml not found")
    
    return conflicts

def fix_config_conflicts():
    """Fix configuration conflicts."""
    print("\n🔧 Fixing Configuration Conflicts")
    print("=" * 50)
    
    # 1. Fix .env file
    print("\n1. Fixing .env file...")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Remove placeholder keys
        content = content.replace("GROQ_API_KEY=your-groq-key-here", "# GROQ_API_KEY=your-groq-key-here")
        content = content.replace("MISTRAL_API_KEY=your-mistral-key-here", "# MISTRAL_API_KEY=your-mistral-key-here")
        
        # Remove hardcoded provider (let UI control it)
        content = content.replace("DEFAULT_LLM_PROVIDER=gemini", "# DEFAULT_LLM_PROVIDER=gemini")
        content = content.replace("DEFAULT_LLM_MODEL=gemini-1.5-flash", "# DEFAULT_LLM_MODEL=gemini-1.5-flash")
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file fixed - removed placeholders and hardcoded provider")
    else:
        print("ℹ️ .env file not found")
    
    # 2. Fix config.ini
    print("\n2. Fixing config.ini...")
    ini_file = Path("config.ini")
    if ini_file.exists():
        with open(ini_file, 'r') as f:
            content = f.read()
        
        # Comment out hardcoded provider
        content = content.replace("provider = gemini", "# provider = gemini")
        content = content.replace("model = gemini-1.5-flash", "# model = gemini-1.5-flash")
        
        with open(ini_file, 'w') as f:
            f.write(content)
        
        print("✅ config.ini fixed - commented out hardcoded provider")
    else:
        print("ℹ️ config.ini not found")
    
    # 3. Update config.yaml with proper settings
    print("\n3. Updating config.yaml...")
    config_manager = ConfigManager()
    
    # Get current config
    config = config_manager.load()
    
    # Update with proper structure
    config.update({
        "current_provider": "groq",  # Set to Groq as requested
        "current_model": "llama3-8b-8192",  # Set to Groq model
        "api_keys": {
            "groq": "gsk_your-actual-groq-key-here",  # Placeholder for user to fill
            "gemini": config.get("api_keys", {}).get("gemini", ""),
            "openai": config.get("api_keys", {}).get("openai", ""),
            "anthropic": config.get("api_keys", {}).get("anthropic", ""),
            "mistral": config.get("api_keys", {}).get("mistral", "")
        }
    })
    
    # Save updated config
    config_manager.save(config)
    print("✅ config.yaml updated with Groq as default provider")
    
    print("\n🎯 Configuration conflicts fixed!")
    print("Next steps:")
    print("1. Edit ~/.atlas/config.yaml and replace 'gsk_your-actual-groq-key-here' with your real Groq API key")
    print("2. Restart Atlas")
    print("3. Your Groq settings should now persist!")

def show_current_priority():
    """Show current configuration priority."""
    print("\n📊 Current Configuration Priority")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    print("Priority order (highest to lowest):")
    print("1. .env file")
    print("2. config.ini")
    print("3. ~/.atlas/config.yaml")
    print("4. Environment variables")
    print("5. Default values")
    
    print("\nCurrent values:")
    print(f"Provider: {config_manager.get_current_provider()}")
    print(f"Model: {config_manager.get_current_model()}")
    print(f"Groq API Key: {config_manager.get_groq_api_key()[:10] if config_manager.get_groq_api_key() else 'Not set'}...")
    print(f"Gemini API Key: {config_manager.get_gemini_api_key()[:10] if config_manager.get_gemini_api_key() else 'Not set'}...")

def main():
    """Main function."""
    print("🔧 Atlas Configuration Conflict Fixer")
    print("=" * 60)
    
    # Check for conflicts
    conflicts = check_config_conflicts()
    
    if conflicts:
        print("\n🚨 Conflicts found:")
        for conflict in conflicts:
            print(f"  {conflict}")
        
        print(f"\nFound {len(conflicts)} configuration conflicts!")
        
        # Show current priority
        show_current_priority()
        
        # Ask user if they want to fix
        response = input("\nDo you want to fix these conflicts? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            fix_config_conflicts()
        else:
            print("No changes made.")
    else:
        print("\n✅ No configuration conflicts found!")
        show_current_priority()

if __name__ == "__main__":
    main() 