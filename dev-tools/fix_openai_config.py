#!/usr/bin/env python3
"""
Fix OpenAI Configuration Issues

This script fixes OpenAI API key configuration issues in Atlas,
allowing the system to work properly with Gemini as the default
while gracefully handling missing OpenAI keys.
"""

import os
import sys
import configparser
from pathlib import Path

def fix_openai_config():
    """Fix OpenAI configuration issues"""
    atlas_dir = Path(__file__).parent
    config_path = atlas_dir / "config.ini"
    env_path = atlas_dir / ".env"
    
    print("🔧 Fixing OpenAI Configuration Issues...")
    print(f"Atlas Directory: {atlas_dir}")
    
    #Read current config
    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path)
        print(f"✅ Found config.ini at: {config_path}")
    else:
        print(f"❌ No config.ini found at: {config_path}")
        return False
    
    #Check current OpenAI settings
    openai_key = config.get('OpenAI', 'api_key', fallback='')
    openai_model = config.get('OpenAI', 'model_name', fallback='gpt-4-turbo')
    
    print(f"Current OpenAI API Key: {openai_key[:20]}..." if len(openai_key) > 20 else f"Current OpenAI API Key: {openai_key}")
    print(f"Current OpenAI Model: {openai_model}")
    
    #Check if OpenAI key is placeholder
    is_placeholder = (not openai_key or 
                     openai_key == "YOUR_OPENAI_API_KEY_HERE" or
                     openai_key == "sk-your-openai-key-here" or
                     openai_key.startswith("sk-placeholder") or
                     "placeholder" in openai_key.lower())
    
    if is_placeholder:
        print("⚠️  OpenAI API key is a placeholder")
        
        #Check environment variable
        env_openai_key = os.getenv('OPENAI_API_KEY', '')
        if env_openai_key and not any(x in env_openai_key.lower() for x in ['placeholder', 'your-', 'here']):
            print(f"✅ Found valid OpenAI key in environment: {env_openai_key[:20]}...")
            #Update config with env key
            config.set('OpenAI', 'api_key', env_openai_key)
            with open(config_path, 'w') as f:
                config.write(f)
            print("✅ Updated config.ini with environment OpenAI key")
        else:
            print("ℹ️  No valid OpenAI key found in environment")
            
            #Set a clear placeholder that won't cause errors
            safe_placeholder = "#OpenAI key not configured - using Gemini as default"
            config.set('OpenAI', 'api_key', safe_placeholder)
            
            #Ensure we have a comment about this
            if not config.has_option('OpenAI', 'note'):
                config.set('OpenAI', 'note', 'OpenAI is optional when using Gemini as default provider')
            
            with open(config_path, 'w') as f:
                config.write(f)
            print("✅ Set safe placeholder for OpenAI key")
    else:
        print("✅ OpenAI API key appears to be valid")
    
    #Ensure Gemini is still the default
    current_provider = config.get('LLM', 'provider', fallback='gemini')
    current_model = config.get('LLM', 'model', fallback='gemini-1.5-flash')
    
    if current_provider.lower() != 'gemini':
        print(f"⚠️  LLM provider is {current_provider}, changing to gemini")
        config.set('LLM', 'provider', 'gemini')
        config.set('LLM', 'model', 'gemini-1.5-flash')
        with open(config_path, 'w') as f:
            config.write(f)
        print("✅ Reset LLM provider to Gemini")
    else:
        print(f"✅ LLM provider is correctly set to: {current_provider}")
        print(f"✅ LLM model is: {current_model}")
    
    #Update .env file if needed
    if env_path.exists():
        print(f"✅ Found .env file at: {env_path}")
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        #Check if we need to update .env
        needs_update = False
        lines = env_content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.startswith('OPENAI_API_KEY=') and is_placeholder:
                #Comment out placeholder OpenAI key
                new_lines.append(f"#{line}  # Placeholder - not configured")
                needs_update = True
            elif line.startswith('DEFAULT_LLM_PROVIDER=') and not line.endswith('gemini'):
                new_lines.append('DEFAULT_LLM_PROVIDER=gemini')
                needs_update = True
            elif line.startswith('DEFAULT_LLM_MODEL=') and 'gemini' not in line:
                new_lines.append('DEFAULT_LLM_MODEL=gemini-1.5-flash')
                needs_update = True
            else:
                new_lines.append(line)
        
        if needs_update:
            with open(env_path, 'w') as f:
                f.write('\n'.join(new_lines))
            print("✅ Updated .env file")
        else:
            print("✅ .env file is already correct")
    
    print("\n🎯 OpenAI Configuration Fix Summary:")
    print("=" * 50)
    print(f"• OpenAI API Key: {'Placeholder (safe)' if is_placeholder else 'Configured'}")
    print(f"• Default Provider: {config.get('LLM', 'provider', fallback='gemini')}")
    print(f"• Default Model: {config.get('LLM', 'model', fallback='gemini-1.5-flash')}")
    print(f"• Gemini API Key: {'Configured' if config.get('Gemini', 'api_key', fallback='') else 'Missing'}")
    
    if is_placeholder:
        print("\nℹ️  Note: OpenAI functionality will be limited without a valid API key.")
        print("   Atlas will continue to work normally with Gemini as the default provider.")
        print("   To enable OpenAI features, set a valid OPENAI_API_KEY in your environment.")
    
    return True

def main():
    """Main function"""
    try:
        success = fix_openai_config()
        if success:
            print("\n✅ OpenAI configuration fixes completed successfully!")
            return 0
        else:
            print("\n❌ Failed to fix OpenAI configuration")
            return 1
    except Exception as e:
        print(f"\n❌ Error fixing OpenAI configuration: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
