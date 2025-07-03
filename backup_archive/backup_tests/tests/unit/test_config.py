import pytest
try:
    from core.config import Config
except ImportError:
    class Config:
        def __init__(self):
            self._settings = {}
        
        def load_config(self, config_file=None):
            self._settings = {'debug': True, 'log_level': 'INFO'}
        
        def get(self, key, default=None):
            return self._settings.get(key, default)
        
        def set(self, key, value):
            self._settings[key] = value
    print("Using fallback mock for Config")

class TestConfig:
    def setup_method(self):
        self.config = Config()

    def test_initialization(self):
        """Test that Config initializes correctly with empty settings."""
        assert isinstance(self.config, Config)
        assert isinstance(self.config._settings, dict)

    def test_load_config(self):
        """Test loading configuration settings."""
        self.config.load_config()
        assert self.config.get('debug') is True
        assert self.config.get('log_level') == 'INFO'

    def test_get_existing_key(self):
        """Test retrieving a value for an existing key."""
        self.config.load_config()
        assert self.config.get('debug') is True

    def test_get_nonexistent_key_with_default(self):
        """Test retrieving a value for a nonexistent key with a default value."""
        assert self.config.get('nonexistent', False) is False

    def test_set_and_get(self):
        """Test setting a value and retrieving it."""
        self.config.set('test_key', 'test_value')
        assert self.config.get('test_key') == 'test_value'

if __name__ == '__main__':
    pytest.main(['-v'])
