#!/usr/bin/env python3
"""
Simple test for UI settings save
"""

from utils.config_manager import ConfigManager


def test_ui_save():
    """Test saving settings from UI values."""
    print("🔧 Testing UI Settings Save")
    print("=" * 50)

    config_manager = ConfigManager()

    # Simulate UI values (like from main.py)
    ui_groq_key = "gsk_test-ui-groq-key-123"
    ui_provider = "groq"
    ui_model = "llama3-8b-8192"

    print("UI Values:")
    print(f"  Groq Key: {ui_groq_key}")
    print(f"  Provider: {ui_provider}")
    print(f"  Model: {ui_model}")

    # Create settings like main.py _save_settings function
    settings = {
        "current_provider": ui_provider,
        "current_model": ui_model,
        "api_keys": {
            "groq": ui_groq_key,
            "gemini": "",
            "openai": "",
            "anthropic": "",
            "mistral": "",
        },
        "plugins_enabled": {},
        "security": {
            "destructive_op_threshold": 80,
            "api_usage_threshold": 50,
            "file_access_threshold": 70,
            "rules": [],
            "notifications": {"email": False, "telegram": False, "sms": False},
        },
        "agents": {},
    }

    # Save settings
    print("\n1. Saving settings...")
    config_manager.save(settings)
    print("   ✅ Settings saved")

    # Load settings back
    print("\n2. Loading settings...")
    loaded_settings = config_manager.load()

    # Check if values match
    loaded_provider = loaded_settings.get("current_provider")
    loaded_model = loaded_settings.get("current_model")
    loaded_groq_key = loaded_settings.get("api_keys", {}).get("groq")

    print(f"   Loaded Provider: {loaded_provider}")
    print(f"   Loaded Model: {loaded_model}")
    print(f"   Loaded Groq Key: {loaded_groq_key[:10]}...")

    # Verify
    success = True
    if loaded_provider != ui_provider:
        print(f"   ❌ Provider mismatch: expected {ui_provider}, got {loaded_provider}")
        success = False
    else:
        print("   ✅ Provider matches")

    if loaded_model != ui_model:
        print(f"   ❌ Model mismatch: expected {ui_model}, got {loaded_model}")
        success = False
    else:
        print("   ✅ Model matches")

    if loaded_groq_key != ui_groq_key:
        print(f"   ❌ Groq key mismatch: expected {ui_groq_key}, got {loaded_groq_key}")
        success = False
    else:
        print("   ✅ Groq key matches")

    # Check file content
    print("\n3. Checking config file...")
    config_path = config_manager.path
    with open(config_path, "r") as f:
        content = f.read()

    if (
        "groq" in content
        and "llama3-8b-8192" in content
        and "gsk_test-ui-groq-key-123" in content
    ):
        print("   ✅ Config file contains correct values")
    else:
        print("   ❌ Config file missing correct values")
        success = False

    return success


def cleanup():
    """Clean up test settings."""
    print("\n🧹 Cleaning up...")
    config_manager = ConfigManager()

    # Reset to defaults
    default_settings = {
        "current_provider": "gemini",
        "current_model": "gemini-1.5-flash",
        "api_keys": {
            "groq": "",
            "gemini": "",
            "openai": "",
            "anthropic": "",
            "mistral": "",
        },
    }

    config_manager.save(default_settings)
    print("✅ Cleanup completed")


def main():
    """Main test function."""
    print("🔧 UI Settings Save Test")
    print("=" * 60)

    try:
        success = test_ui_save()

        if success:
            print("\n🎉 Test passed! UI settings save is working correctly.")
        else:
            print("\n⚠️ Test failed. Check the output above.")

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        success = False

    finally:
        cleanup()


if __name__ == "__main__":
    main()
