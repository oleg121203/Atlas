import json
from pathlib import Path
from typing import Any, Dict, Union

import yaml

from utils.logger import get_logger

logger = get_logger()

CONFIG_DIR = Path.home() / ".atlas"
CONFIG_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"


class ConfigManager:
    """Handles reading and writing configuration files."""

    def __init__(self, path: Union[Path, None] = None) -> None:
        self.path = Path(path) if path else DEFAULT_CONFIG_PATH
        if not self.path.exists():
            self._create_default()

    def load(self) -> Dict[str, Any]:
        """Return the parsed configuration as a dictionary."""
        try:
            with self.path.open("r", encoding="utf-8") as f:
                if self.path.suffix == ".json":
                    return json.load(f)
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config from {self.path}: {e}. Creating default.")
            self._create_default()
            return self.load()

    def save(self, data: Dict[str, Any]) -> None:
        """Persist configuration to disk."""
        try:
            with self.path.open("w", encoding="utf-8") as f:
                if self.path.suffix == ".json":
                    json.dump(data, f, indent=2)
                else:
                    yaml.safe_dump(data, f, sort_keys=False)
            logger.info(f"Configuration saved to {self.path}")
        except (OSError, yaml.YAMLError) as e:
            logger.error(f"Failed to save config to {self.path}: {e}")

    def get_app_data_path(self, subdirectory_name: str) -> Path:
        """Return the path to a subdirectory in the app data dir, creating it if needed."""
        data_path = CONFIG_DIR / subdirectory_name
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path

    def get_memory_db_path(self) -> str:
        """Return the path to the memory database, creating the directory if needed."""
        memory_path = self.get_app_data_path("memory")
        return str(memory_path)

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key from .env file, config, or environment."""
        import os
        config = self.load()
        #Пріоритет: .env файл → конфіг → змінні середовища
        key = (os.getenv("OPENAI_API_KEY", "") or
               config.get("openai_api_key", "") or
               config.get("api_keys", {}).get("openai", ""))
        return key

    def get_gemini_api_key(self) -> str:
        """Get Gemini API key from .env file, config, or environment."""
        import os
        config = self.load()
        #Пріоритет: .env файл → конфіг → змінні середовища
        key = (os.getenv("GEMINI_API_KEY", "") or
               config.get("gemini_api_key", "") or
               config.get("api_keys", {}).get("gemini", ""))
        return key

    def get_groq_api_key(self) -> str:
        """Get Groq API key from .env file, config, or environment."""
        import os
        config = self.load()
        #Пріоритет: .env файл → конфіг → змінні середовища
        key = (os.getenv("GROQ_API_KEY", "") or
               config.get("groq_api_key", "") or
               config.get("api_keys", {}).get("groq", ""))
        return key

    def get_mistral_api_key(self) -> str:
        """Get Mistral API key from .env file, config, or environment."""
        import os
        config = self.load()
        #Пріоритет: .env файл → конфіг → змінні середовища
        key = (os.getenv("MISTRAL_API_KEY", "") or
               config.get("mistral_api_key", "") or
               config.get("api_keys", {}).get("mistral", ""))
        return key

    def get_current_provider(self) -> str:
        """Get current LLM provider from .env file or config."""
        import os
        config = self.load()
        #Пріоритет: .env файл → конфіг
        return (os.getenv("DEFAULT_LLM_PROVIDER", "") or
                config.get("current_provider", "gemini"))

    def get_current_model(self) -> str:
        """Get current LLM model from .env file or config."""
        import os
        config = self.load()
        #Пріоритет: .env файл → конфіг
        return (os.getenv("DEFAULT_LLM_MODEL", "") or
                config.get("current_model", "gemini-1.5-flash"))

    def get_model_name(self) -> str:
        """Get model name (alias for get_current_model)."""
        return self.get_current_model()

    def get_setting(self, key: str, default=None):
        """Get a setting from config with fallback to default."""
        config = self.load()

        #Handle API keys specially
        if key == "groq_api_key":
            return self.get_groq_api_key()
        if key == "mistral_api_key":
            return self.get_mistral_api_key()
        if key == "gemini_api_key":
            return self.get_gemini_api_key()
        if key == "openai_api_key":
            return self.get_openai_api_key()

        return config.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set a setting in config and save to disk."""
        config = self.load()
        config[key] = value
        self.save(config)

    def set_llm_provider_and_model(self, provider: str, model: str):
        """Set LLM provider and model in configuration."""
        try:
            config = self.load()

            if provider:
                config["current_provider"] = provider
                logger.info(f"Set LLM provider to: {provider}")

            if model:
                config["current_model"] = model
                logger.info(f"Set LLM model to: {model}")

            #Save to disk
            self.save(config)
            logger.info(f"✅ LLM configuration updated: provider={provider}, model={model}")
            return True

        except Exception as e:
            logger.error(f"❌ Error setting LLM provider/model: {e}")
            return False

    def set_llm_api_key(self, provider: str, api_key: str):
        """Set API key for specific LLM provider."""
        try:
            config = self.load()

            #Initialize api_keys section if it doesn't exist
            if "api_keys" not in config:
                config["api_keys"] = {}

            #Set the API key
            config["api_keys"][provider.lower()] = api_key

            #Also set in the direct key format for backwards compatibility
            config[f"{provider.lower()}_api_key"] = api_key

            #Save to disk
            self.save(config)
            logger.info(f"✅ Set {provider} API key")
            return True

        except Exception as e:
            logger.error(f"❌ Error setting {provider} API key: {e}")
            return False

    def _create_default(self) -> None:
        """Write default configuration scaffold."""
        default_cfg = {
            "current_provider": "gemini",
            "current_model": "gemini-1.5-flash",
            "agents": {
                "Browser Agent": {"provider": "gemini", "model": "gemini-1.5-flash", "fallback_chain": []},
                "Screen Agent": {"provider": "gemini", "model": "gemini-1.5-flash", "fallback_chain": []},
                "Text Agent": {"provider": "gemini", "model": "gemini-1.5-flash", "fallback_chain": []},
                "System Interaction Agent": {"provider": "gemini", "model": "gemini-1.5-flash", "fallback_chain": []},
            },
            "security": {
                "destructive_op_threshold": 80,
                "api_usage_threshold": 50,
                "file_access_threshold": 70,
                "rules": [
                    "#Example Rule: Deny all shell commands that contain 'rm -rf'",
                    "DENY,TERMINAL,.*rm -rf.*",
                ],
            },
        }
        self.save(default_cfg)


#Global instance for backward compatibility
config_manager = ConfigManager()
