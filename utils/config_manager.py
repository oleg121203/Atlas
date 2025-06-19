import configparser
import os
import logging
import yaml
from typing import Any, Optional, Dict

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        
        # Використовуємо той самий YAML файл, що й основний ConfigManager
        self.yaml_config_file = os.path.expanduser('~/.atlas/config.yaml')
        self.yaml_config = {}
        
        self._load_configs()

    def _load_configs(self):
        """Load both INI and YAML configurations."""
        # Load INI config
        if not os.path.exists(self.config_file):
            self.logger.warning(f"'{self.config_file}' not found. Please create it from 'config.ini.example'.")
            self._create_default_config()
        else:
            self.config.read(self.config_file)
            
        # Load YAML config
        if os.path.exists(self.yaml_config_file):
            try:
                with open(self.yaml_config_file, 'r') as f:
                    self.yaml_config = yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.warning(f"Failed to load YAML config: {e}")
                self.yaml_config = {}

    def _create_default_config(self):
        """Creates a default config object for when the file is missing."""
        self.config['OpenAI'] = {
            'API_KEY': 'YOUR_OPENAI_API_KEY_HERE',
            'MODEL_NAME': 'gpt-4-turbo'
        }
        self.config['Gemini'] = {
            'API_KEY': 'YOUR_GEMINI_API_KEY_HERE',
            'MODEL_NAME': 'gemini-1.5-flash'
        }
        self.config['LLM'] = {
            'provider': 'gemini',
            'model': 'gemini-1.5-flash'
        }
        self.config['App'] = {
            'DEFAULT_GOAL': 'Analyze the current screen and suggest the next action.'
        }

    def get(self, section, key, fallback=None):
        """Get a value from the INI config file."""
        return self.config.get(section, key, fallback=fallback)
        
    def get_setting(self, key: str, fallback: Any = None) -> Any:
        """Get a setting from YAML config with fallback to INI config."""
        # Handle API keys specially
        if key == 'openai_api_key':
            return self.get_openai_api_key()
        elif key == 'gemini_api_key':
            return self.get_gemini_api_key()
        elif key == 'groq_api_key':
            return self.get_groq_api_key()
        elif key == 'mistral_api_key':
            return self.get_mistral_api_key()
        elif key == 'anthropic_api_key':
            return self.get_anthropic_api_key()
            
        # Try YAML first
        if key in self.yaml_config:
            return self.yaml_config[key]
            
        # Try INI format (section.key)
        if '.' in key:
            section, ini_key = key.split('.', 1)
            return self.get(section, ini_key, fallback)
            
        return fallback

    def set_setting(self, key: str, value: Any):
        """Set a setting in YAML config."""
        self.yaml_config[key] = value
        self._save_yaml_config()
        
    def _save_yaml_config(self):
        """Save YAML config to file."""
        try:
            os.makedirs(os.path.dirname(self.yaml_config_file), exist_ok=True)
            with open(self.yaml_config_file, 'w') as f:
                yaml.dump(self.yaml_config, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"Failed to save YAML config: {e}")

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from config or environment."""
        import os
        # Прямо перевіряємо YAML конфіг без виклику get_setting для уникнення рекурсії
        yaml_key = self.yaml_config.get('openai_api_key', '')
        ini_key = self.get('OpenAI', 'API_KEY', '')
        env_key = os.getenv('OPENAI_API_KEY', '')
        return yaml_key or ini_key or env_key

    def get_current_provider(self) -> str:
        """Get current LLM provider from config."""
        return self.get_setting('current_provider', 'gemini')

    def get_current_model(self) -> str:
        """Get current LLM model from config."""
        return self.get_setting('current_model', 'gemini-1.5-flash')
        
    def get_model_name(self) -> str:
        """Get model name (alias for get_current_model)."""
        return self.get_current_model()

    def load(self) -> Dict[str, Any]:
        """Load all settings from YAML config."""
        self._load_configs()  # Reload from disk
        return self.yaml_config.copy()
        
    def save(self, settings: Dict[str, Any]):
        """Save settings to YAML config."""
        self.yaml_config.update(settings)
        self._save_yaml_config()

    def get_llm_api_keys(self) -> Dict[str, Optional[str]]:
        """Get all LLM API keys."""
        return {
            'openai': self.get_openai_api_key(),
            'gemini': self.get_gemini_api_key(),
            'groq': self.get_groq_api_key(),
            'mistral': self.get_mistral_api_key(),
            'anthropic': self.get_anthropic_api_key(),
        }
        
    def set_llm_api_key(self, provider: str, api_key: str):
        """Set an API key for a specific provider."""
        if provider == 'openai':
            # Save to both INI and YAML for backward compatibility
            if not self.config.has_section('OpenAI'):
                self.config.add_section('OpenAI')
            self.config.set('OpenAI', 'API_KEY', api_key)
            try:
                with open(self.config_file, 'w') as f:
                    self.config.write(f)
            except Exception as e:
                self.logger.error(f"Failed to save INI config: {e}")
                
        # Always save to YAML
        self.set_setting(f'{provider}_api_key', api_key)

    def get_gemini_api_key(self) -> str:
        """Get Gemini API key from config or environment."""
        import os
        yaml_key = self.yaml_config.get('gemini_api_key', '')
        env_key = os.getenv('GEMINI_API_KEY', '')
        return yaml_key or env_key

    def get_groq_api_key(self) -> str:
        """Get Groq API key from config or environment."""
        import os
        yaml_key = self.yaml_config.get('groq_api_key', '')
        env_key = os.getenv('GROQ_API_KEY', '')
        return yaml_key or env_key

    def get_mistral_api_key(self) -> str:
        """Get Mistral API key from config or environment."""
        import os
        yaml_key = self.yaml_config.get('mistral_api_key', '')
        env_key = os.getenv('MISTRAL_API_KEY', '')
        return yaml_key or env_key

    def get_anthropic_api_key(self) -> str:
        """Get Anthropic API key from config or environment."""
        import os
        yaml_key = self.yaml_config.get('anthropic_api_key', '')
        env_key = os.getenv('ANTHROPIC_API_KEY', '')
        return yaml_key or env_key

    def set_llm_provider_and_model(self, provider: str, model: str):
        """Set LLM provider and model in configuration."""
        try:
            # Update INI config
            if not self.config.has_section('LLM'):
                self.config.add_section('LLM')
            
            if provider:
                self.config.set('LLM', 'provider', provider)
                self.logger.info(f"Set LLM provider to: {provider}")
            
            if model:
                self.config.set('LLM', 'model', model)
                self.logger.info(f"Set LLM model to: {model}")
            
            # Save INI config
            try:
                with open(self.config_file, 'w') as configfile:
                    self.config.write(configfile)
                self.logger.info(f"Saved LLM settings to {self.config_file}")
            except Exception as e:
                self.logger.error(f"Failed to save INI config: {e}")
            
            # Also update YAML config
            if provider:
                self.set_setting('current_provider', provider)
            if model:
                self.set_setting('current_model', model)
                
            self.logger.info(f"✅ LLM configuration updated: provider={provider}, model={model}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error setting LLM provider/model: {e}")
            return False

    def set_llm_api_key(self, provider: str, api_key: str):
        """Set API key for specific LLM provider in INI config."""
        try:
            section_name = provider.title()  # 'gemini' -> 'Gemini'
            
            if not self.config.has_section(section_name):
                self.config.add_section(section_name)
            
            self.config.set(section_name, 'api_key', api_key)
            
            # Save INI config
            try:
                with open(self.config_file, 'w') as configfile:
                    self.config.write(configfile)
                self.logger.info(f"Saved {provider} API key to {self.config_file}")
            except Exception as e:
                self.logger.error(f"Failed to save INI config: {e}")
            
            # Also save to YAML config
            self.set_setting(f'{provider.lower()}_api_key', api_key)
            
            self.logger.info(f"✅ Set {provider} API key")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error setting {provider} API key: {e}")
            return False

# Global instance
config_manager = ConfigManager()
