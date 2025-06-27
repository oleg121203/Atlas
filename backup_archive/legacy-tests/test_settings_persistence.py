#!/usr/bin/env python3
"""
Test script for settings persistence
"""

from utils.config_manager import ConfigManager


def test_settings_persistence():
    """Test that settings are properly saved and loaded."""
    print("🔧 Testing Settings Persistence")
    print("=" * 50)

    # Create a test config manager
    config_manager = ConfigManager()

    # Test data
    test_settings = {
        "current_provider": "groq",
        "current_model": "llama3-8b-8192",
        "api_keys": {
            "openai": "sk-test-openai-key",
            "gemini": "test-gemini-key",
            "groq": "gsk_test-groq-key",
            "mistral": "test-mistral-key",
            "anthropic": "sk-ant-test-key",
        },
        "plugins_enabled": {"unified_browser": True, "weather_tool": False},
        "security": {
            "destructive_op_threshold": 85,
            "api_usage_threshold": 75,
            "file_access_threshold": 60,
            "rules": ["DENY,TERMINAL,.*rm -rf.*"],
            "notifications": {"email": True, "telegram": False, "sms": False},
        },
        "agents": {
            "Browser Agent": {
                "provider": "groq",
                "model": "llama3-8b-8192",
                "fallback_chain": ["gemini", "openai"],
            }
        },
    }

    print("📝 Saving test settings...")
    try:
        config_manager.save(test_settings)
        print("✅ Settings saved successfully")
    except Exception as e:
        print(f"❌ Failed to save settings: {e}")
        return False

    print("\n📖 Loading settings...")
    try:
        loaded_settings = config_manager.load()
        print("✅ Settings loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        return False

    print("\n🔍 Verifying settings...")

    # Check current provider and model
    current_provider = loaded_settings.get("current_provider")
    current_model = loaded_settings.get("current_model")

    print(f"   Current provider: {current_provider} (expected: groq)")
    print(f"   Current model: {current_model} (expected: llama3-8b-8192)")

    if current_provider != "groq":
        print("   ❌ Current provider not saved correctly")
        return False
    if current_model != "llama3-8b-8192":
        print("   ❌ Current model not saved correctly")
        return False

    # Check API keys
    api_keys = loaded_settings.get("api_keys", {})
    groq_key = api_keys.get("groq")
    print(f"   Groq API key: {groq_key[:10]}... (expected: gsk_test-groq-key)")

    if groq_key != "gsk_test-groq-key":
        print("   ❌ Groq API key not saved correctly")
        return False

    # Check plugins
    plugins = loaded_settings.get("plugins_enabled", {})
    unified_browser = plugins.get("unified_browser")
    weather_tool = plugins.get("weather_tool")

    print(f"   Unified browser plugin: {unified_browser} (expected: True)")
    print(f"   Weather tool plugin: {weather_tool} (expected: False)")

    if not unified_browser or weather_tool:
        print("   ❌ Plugin settings not saved correctly")
        return False

    # Check security settings
    security = loaded_settings.get("security", {})
    destructive_threshold = security.get("destructive_op_threshold")
    notifications = security.get("notifications", {})
    email_notifications = notifications.get("email")

    print(f"   Destructive threshold: {destructive_threshold} (expected: 85)")
    print(f"   Email notifications: {email_notifications} (expected: True)")

    if destructive_threshold != 85 or not email_notifications:
        print("   ❌ Security settings not saved correctly")
        return False

    # Check agents
    agents = loaded_settings.get("agents", {})
    browser_agent = agents.get("Browser Agent", {})
    agent_provider = browser_agent.get("provider")
    agent_model = browser_agent.get("model")

    print(f"   Browser agent provider: {agent_provider} (expected: groq)")
    print(f"   Browser agent model: {agent_model} (expected: llama3-8b-8192)")

    if agent_provider != "groq" or agent_model != "llama3-8b-8192":
        print("   ❌ Agent settings not saved correctly")
        return False

    print("\n✅ All settings verified successfully!")
    return True


def test_config_manager_methods():
    """Test ConfigManager methods directly."""
    print("\n🔧 Testing ConfigManager Methods")
    print("=" * 50)

    config_manager = ConfigManager()

    # Test setting and getting API keys
    print("Testing API key methods...")

    # Set Groq API key
    success = config_manager.set_llm_api_key("groq", "gsk_test-groq-key-123")
    print(f"   Set Groq API key: {'✅' if success else '❌'}")

    # Get Groq API key
    groq_key = config_manager.get_groq_api_key()
    print(f"   Retrieved Groq API key: {groq_key[:10]}...")

    if groq_key != "gsk_test-groq-key-123":
        print("   ❌ API key not retrieved correctly")
        return False

    # Test setting provider and model
    print("\nTesting provider and model methods...")

    success = config_manager.set_llm_provider_and_model("groq", "llama3-8b-8192")
    print(f"   Set provider and model: {'✅' if success else '❌'}")

    current_provider = config_manager.get_current_provider()
    current_model = config_manager.get_current_model()

    print(f"   Current provider: {current_provider}")
    print(f"   Current model: {current_model}")

    if current_provider != "groq" or current_model != "llama3-8b-8192":
        print("   ❌ Provider/model not set correctly")
        return False

    print("\n✅ All ConfigManager methods working correctly!")
    return True


def test_config_file_location():
    """Test config file location and format."""
    print("\n📁 Testing Config File Location")
    print("=" * 50)

    config_manager = ConfigManager()

    # Check config file path
    config_path = config_manager.path
    print(f"Config file path: {config_path}")

    # Check if file exists
    if config_path.exists():
        print("✅ Config file exists")

        # Check file size
        file_size = config_path.stat().st_size
        print(f"   File size: {file_size} bytes")

        # Check file format
        if config_path.suffix == ".yaml":
            print("   Format: YAML")
        elif config_path.suffix == ".json":
            print("   Format: JSON")
        else:
            print(f"   Format: {config_path.suffix}")

        # Show first few lines
        try:
            with open(config_path, "r") as f:
                lines = f.readlines()[:5]
                print("   First few lines:")
                for i, line in enumerate(lines, 1):
                    print(f"     {i}: {line.strip()}")
        except Exception as e:
            print(f"   ❌ Could not read file: {e}")
    else:
        print("❌ Config file does not exist")
        return False

    return True


def cleanup_test_settings():
    """Clean up test settings."""
    print("\n🧹 Cleaning up test settings...")

    config_manager = ConfigManager()

    # Reset to default settings
    default_settings = {
        "current_provider": "gemini",
        "current_model": "gemini-1.5-flash",
        "api_keys": {},
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

    try:
        config_manager.save(default_settings)
        print("✅ Test settings cleaned up")
    except Exception as e:
        print(f"❌ Failed to clean up: {e}")


def main():
    """Main test function."""
    print("🔧 Settings Persistence Test Suite")
    print("=" * 60)

    # Run all tests
    tests = [
        ("Settings Persistence", test_settings_persistence),
        ("ConfigManager Methods", test_config_manager_methods),
        ("Config File Location", test_config_file_location),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Settings persistence is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    # Cleanup
    cleanup_test_settings()

    return passed == total


if __name__ == "__main__":
    main()
