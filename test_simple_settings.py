#!/usr/bin/env python3
"""
Simple test for settings persistence
"""

from utils.config_manager import ConfigManager
import time

def test_simple_settings():
    """Test simple settings save and load."""
    print("🔧 Testing Simple Settings Save/Load")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    # Test 1: Save Groq settings
    print("1. Saving Groq settings...")
    test_settings = {
        "current_provider": "groq",
        "current_model": "llama3-8b-8192",
        "api_keys": {
            "groq": "gsk_test-groq-key-123",
            "gemini": "",
            "openai": "",
            "anthropic": "",
            "mistral": ""
        }
    }
    
    config_manager.save(test_settings)
    print("   ✅ Settings saved")
    
    # Test 2: Load settings
    print("2. Loading settings...")
    loaded_settings = config_manager.load()
    
    current_provider = loaded_settings.get("current_provider")
    current_model = loaded_settings.get("current_model")
    groq_key = loaded_settings.get("api_keys", {}).get("groq")
    
    print(f"   Provider: {current_provider}")
    print(f"   Model: {current_model}")
    print(f"   Groq Key: {groq_key[:10]}...")
    
    # Test 3: Verify
    if current_provider == "groq" and current_model == "llama3-8b-8192" and groq_key == "gsk_test-groq-key-123":
        print("   ✅ All settings loaded correctly")
    else:
        print("   ❌ Settings not loaded correctly")
        return False
    
    # Test 4: Check file content
    print("3. Checking config file...")
    config_path = config_manager.path
    print(f"   Config file: {config_path}")
    print(f"   File exists: {config_path.exists()}")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
            if "groq" in content and "llama3-8b-8192" in content:
                print("   ✅ Config file contains correct settings")
            else:
                print("   ❌ Config file missing correct settings")
                return False
    
    print("\n✅ Simple settings test passed!")
    return True

def test_config_manager_methods():
    """Test ConfigManager methods."""
    print("\n🔧 Testing ConfigManager Methods")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    # Test set_llm_provider_and_model
    print("1. Testing set_llm_provider_and_model...")
    success = config_manager.set_llm_provider_and_model("groq", "llama3-8b-8192")
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test get_current_provider and get_current_model
    print("2. Testing get methods...")
    provider = config_manager.get_current_provider()
    model = config_manager.get_current_model()
    print(f"   Provider: {provider}")
    print(f"   Model: {model}")
    
    if provider == "groq" and model == "llama3-8b-8192":
        print("   ✅ Get methods working correctly")
    else:
        print("   ❌ Get methods not working")
        return False
    
    # Test set_llm_api_key
    print("3. Testing set_llm_api_key...")
    success = config_manager.set_llm_api_key("groq", "gsk_test-groq-key-456")
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test get_groq_api_key
    print("4. Testing get_groq_api_key...")
    groq_key = config_manager.get_groq_api_key()
    print(f"   Groq Key: {groq_key[:10]}...")
    
    if groq_key == "gsk_test-groq-key-456":
        print("   ✅ API key methods working correctly")
    else:
        print("   ❌ API key methods not working")
        return False
    
    print("\n✅ ConfigManager methods test passed!")
    return True

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
            "mistral": ""
        }
    }
    
    config_manager.save(default_settings)
    print("✅ Cleanup completed")

def main():
    """Main test function."""
    print("🔧 Simple Settings Test")
    print("=" * 60)
    
    try:
        # Run tests
        test1_result = test_simple_settings()
        test2_result = test_config_manager_methods()
        
        # Summary
        print("\n📊 Test Results")
        print("=" * 60)
        print(f"Simple Settings Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
        print(f"ConfigManager Methods: {'✅ PASS' if test2_result else '❌ FAIL'}")
        
        if test1_result and test2_result:
            print("\n🎉 All tests passed! Settings persistence is working.")
        else:
            print("\n⚠️ Some tests failed. Check the output above.")
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
    
    finally:
        cleanup()

if __name__ == "__main__":
    main() 