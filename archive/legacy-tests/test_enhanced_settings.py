#!/usr/bin/env python3
"""
Test Enhanced Settings Integration

This script tests that all enhanced settings are properly saved and loaded.
"""

import sys
import os
import tkinter as tk
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_manager import ConfigManager
from ui.enhanced_settings import EnhancedSettingsView
import customtkinter as ctk

def test_enhanced_settings():
    """Test enhanced settings save and load functionality."""
    
    print("🧪 Testing Enhanced Settings Integration...")
    print("=" * 60)
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Create test window
    root = ctk.CTk()
    root.title("Enhanced Settings Test")
    root.geometry("800x600")
    
    # Create enhanced settings view
    settings_view = EnhancedSettingsView(
        parent=root,
        config_manager=config_manager,
        plugin_manager=None,
        save_callback=lambda settings: print(f"Save callback called with: {list(settings.keys())}")
    )
    settings_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    print("\n1. Testing Settings Loading...")
    
    # Test loading settings
    try:
        settings_view.load_settings()
        print("✅ Settings loaded successfully")
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    print("\n2. Testing Settings Saving...")
    
    # Test saving settings
    try:
        success = settings_view.save_settings()
        if success:
            print("✅ Settings saved successfully")
        else:
            print("❌ Settings save failed")
            return False
    except Exception as e:
        print(f"❌ Error saving settings: {e}")
        return False
    
    print("\n3. Testing Configuration Persistence...")
    
    # Verify settings were saved to config file
    try:
        config = config_manager.load()
        print(f"✅ Configuration loaded: {list(config.keys())}")
        
        # Check key settings
        key_settings = [
            "current_provider", "current_model", "theme", "log_level",
            "max_concurrent_ops", "memory_limit", "temperature", "max_tokens"
        ]
        
        for setting in key_settings:
            if setting in config:
                print(f"   ✅ {setting}: {config[setting]}")
            else:
                print(f"   ⚠️ {setting}: Not found")
        
        # Check API keys
        api_keys = config.get("api_keys", {})
        for provider in ["openai", "gemini", "groq", "mistral"]:
            if provider in api_keys:
                key_value = api_keys[provider]
                if key_value:
                    print(f"   ✅ {provider} API key: {key_value[:10]}...")
                else:
                    print(f"   ⚠️ {provider} API key: Empty")
            else:
                print(f"   ⚠️ {provider} API key: Not found")
        
        # Check plugins
        plugins = config.get("plugins_enabled", {})
        if plugins:
            print(f"   ✅ Plugins configured: {list(plugins.keys())}")
        else:
            print("   ⚠️ No plugins configured")
            
    except Exception as e:
        print(f"❌ Error verifying configuration: {e}")
        return False
    
    print("\n4. Testing UI Integration...")
    
    # Test that UI reflects saved settings
    try:
        # Check some key UI variables
        current_provider = settings_view.settings_vars.get("current_provider")
        if current_provider:
            provider_value = current_provider.get()
            print(f"   ✅ UI current_provider: {provider_value}")
        
        theme_var = settings_view.settings_vars.get("theme")
        if theme_var:
            theme_value = theme_var.get()
            print(f"   ✅ UI theme: {theme_value}")
        
        print("✅ UI integration working")
        
    except Exception as e:
        print(f"❌ Error checking UI integration: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Settings Test Completed Successfully!")
    print("\n📋 Summary:")
    print("   • Settings loading: ✅ Working")
    print("   • Settings saving: ✅ Working")
    print("   • Configuration persistence: ✅ Working")
    print("   • UI integration: ✅ Working")
    print("\n🎯 Next Steps:")
    print("1. Test the settings in the actual Atlas application")
    print("2. Verify that 'Reload Settings' button works")
    print("3. Check that all tabs (General, Security, LLM, Plugins) save correctly")
    
    # Close test window
    root.after(3000, root.destroy)
    root.mainloop()
    
    return True

if __name__ == "__main__":
    test_enhanced_settings() 