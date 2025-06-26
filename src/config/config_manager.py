from pydantic import BaseModel, validator
from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path

class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str
    username: str
    password: str
    pool_size: int = 10

    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

class MonitoringConfig(BaseModel):
    enabled: bool = True
    metrics_interval: int = 30
    alert_thresholds: Dict[str, float] = {
        "cpu": 80.0,
        "memory": 85.0,
        "disk": 90.0
    }

class AtlasConfig(BaseModel):
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseConfig
    monitoring: MonitoringConfig
    recovery: Dict[str, Any] = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[AtlasConfig] = None
        self.load_config()

    def load_config(self):
        """Завантажує та валідує конфігурацію"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        self.config = AtlasConfig(**config_data)

    def reload_config(self):
        """Перезавантажує конфігурацію"""
        self.load_config()

    def get(self, key: str, default: Any = None):
        """Отримує значення конфігурації"""
        keys = key.split('.')
        value = self.config.dict()

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value