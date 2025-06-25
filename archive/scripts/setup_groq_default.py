#!/usr/bin/env python3
"""
Setup Groq as default provider for Atlas

This script updates the Atlas configuration to use Groq as the default LLM provider.
"""

import yaml
from pathlib import Path

def setup_groq_default():
    """Set Groq as the default provider in Atlas configuration."""
    
    # Get the config file path
    config_dir = Path.home() / ".atlas"
    config_file = config_dir / "config.yaml"
    
    print("Setting up Groq as default provider...")
    print(f"Config file: {config_file}")
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(exist_ok=True)
    
    # Load existing config or create new one
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
            print("✅ Loaded existing configuration")
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            config = {}
    else:
        config = {}
        print("📝 Creating new configuration file")
    
    # Update the configuration
    config['current_provider'] = 'groq'
    config['current_model'] = 'llama3-8b-8192'
    
    # Ensure API keys section exists
    if 'api_keys' not in config:
        config['api_keys'] = {}
    
    # Set empty Groq API key if not present
    if 'groq' not in config['api_keys']:
        config['api_keys']['groq'] = ''
    
    # Save the configuration
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        print("✅ Configuration updated successfully!")
        print(f"   Current provider: {config['current_provider']}")
        print(f"   Current model: {config['current_model']}")
        print()
        print("📋 Next steps:")
        print("1. Add your Groq API key to the config file:")
        print(f"   Edit: {config_file}")
        print("   Set: api_keys.groq: 'your-groq-api-key-here'")
        print("2. Restart Atlas")
        print("3. Verify Groq is selected in Settings > LLM Settings tab")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_groq_default() 