#!/usr/bin/env python3
"""
Check current Atlas settings
"""

from utils.config_manager import ConfigManager
import os

def check_settings():
    """Check current Atlas settings."""
    print("🔍 Atlas Settings Checker")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    # Check if config file exists
    config_path = config_manager.path
    print(f"Config file: {config_path}")
    print(f"File exists: {config_path.exists()}")
    
    if not config_path.exists():
        print("❌ Config file not found!")
        return False
    
    # Load settings
    try:
        settings = config_manager.load()
        print("✅ Settings loaded successfully")
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    # Display current settings
    print("\n📋 Current Settings:")
    print("-" * 30)
    
    # Provider and model
    current_provider = settings.get("current_provider", "N/A")
    current_model = settings.get("current_model", "N/A")
    print(f"Provider: {current_provider}")
    print(f"Model: {current_model}")
    
    # API keys
    api_keys = settings.get("api_keys", {})
    print("\n🔑 API Keys:")
    for provider, key in api_keys.items():
        if key:
            masked_key = key[:10] + "..." if len(key) > 10 else key
            print(f"  {provider}: {masked_key}")
        else:
            print(f"  {provider}: [not set]")
    
    # Plugins
    plugins = settings.get("plugins_enabled", {})
    enabled_plugins = [name for name, enabled in plugins.items() if enabled]
    disabled_plugins = [name for name, enabled in plugins.items() if not enabled]
    
    print("\n🔌 Plugins:")
    print(f"  Enabled: {', '.join(enabled_plugins) if enabled_plugins else 'none'}")
    print(f"  Disabled: {', '.join(disabled_plugins) if disabled_plugins else 'none'}")
    
    # Security settings
    security = settings.get("security", {})
    print("\n🔒 Security:")
    print(f"  Destructive op threshold: {security.get('destructive_op_threshold', 'N/A')}")
    print(f"  API usage threshold: {security.get('api_usage_threshold', 'N/A')}")
    print(f"  File access threshold: {security.get('file_access_threshold', 'N/A')}")
    
    # Check for common issues
    print("\n🔍 Issue Check:")
    print("-" * 20)
    
    issues = []
    
    # Check if Groq is configured but no key
    if current_provider == "groq":
        groq_key = api_keys.get("groq", "")
        if not groq_key or groq_key == "your-groq-key-here":
            issues.append("❌ Groq selected as provider but no valid API key")
        else:
            print("✅ Groq provider configured with API key")
    
    # Check if provider is set but no corresponding key
    if current_provider in ["openai", "anthropic", "mistral"]:
        provider_key = api_keys.get(current_provider, "")
        if not provider_key:
            issues.append(f"❌ {current_provider} selected but no API key")
    
    # Check for placeholder keys
    for provider, key in api_keys.items():
        if key and "your-" in key and "-key-here" in key:
            issues.append(f"❌ {provider} has placeholder key: {key}")
    
    if not issues:
        print("✅ No issues found")
    else:
        for issue in issues:
            print(issue)
    
    # Recommendations
    print("\n💡 Recommendations:")
    print("-" * 20)
    
    if current_provider == "gemini":
        print("ℹ️  Currently using Gemini (default)")
        if api_keys.get("groq"):
            print("💡 You have a Groq key - consider switching to Groq for better performance")
    
    elif current_provider == "groq":
        if api_keys.get("groq") and "your-" not in api_keys.get("groq", ""):
            print("✅ Groq properly configured")
        else:
            print("💡 Add a valid Groq API key to use Groq provider")
    
    # File permissions
    try:
        with open(config_path, 'r') as f:
            f.read()
        print("✅ Config file is readable")
    except PermissionError:
        print("❌ Config file permission error")
    except Exception as e:
        print(f"❌ Config file access error: {e}")
    
    return True

def main():
    """Main function."""
    try:
        success = check_settings()
        if success:
            print("\n🎉 Settings check completed successfully!")
        else:
            print("\n⚠️ Settings check failed!")
    except Exception as e:
        print(f"\n❌ Error during settings check: {e}")

if __name__ == "__main__":
    main() 