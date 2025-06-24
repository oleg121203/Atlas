class PluginBase:
    def __init__(self):
        self.active = False

    def activate(self, app_context=None):
        self.active = True

    def deactivate(self):
        self.active = False

    def get_widget(self, parent=None):
        """Повертає QWidget для інтеграції у UI (опціонально)."""
        return None

    def get_settings(self):
        """Повертає dict з налаштуваннями плагіна (опціонально)."""
        return {}

    def set_settings(self, settings):
        """Приймає dict з налаштуваннями плагіна (опціонально)."""
        pass

    def settings_widget(self, parent=None):
        """Повертає QWidget для редагування налаштувань (опціонально)."""
        return None

    def info(self):
        """Повертає словник з інформацією про плагін."""
        return {
            "name": self.__class__.__name__,
            "description": "No description",
            "active": self.active
        } 