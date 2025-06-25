import os
import importlib.util
import sys
from plugins.base import PluginBase

class PluginManager:
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = {}  # name: instance
        self.load_plugins()

    def load_plugins(self):
        for fname in os.listdir(self.plugins_dir):
            if fname.endswith(".py") and fname != "base.py":
                path = os.path.join(self.plugins_dir, fname)
                name = fname[:-3]
                spec = importlib.util.spec_from_file_location(name, path)
                if spec is None or spec.loader is None:
                    print(f"[PluginManager] Failed to load {fname}: spec or loader is None")
                    continue
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                            instance = obj()
                            self.plugins[name] = instance
                except Exception as e:
                    print(f"[PluginManager] Failed to load {fname}: {e}")

    def reload_plugin(self, name):
        """Hot-reload a single plugin by name."""
        fname = f"{name}.py"
        path = os.path.join(self.plugins_dir, fname)
        if not os.path.exists(path):
            print(f"[PluginManager] Plugin file not found: {fname}")
            return
        if name in sys.modules:
            del sys.modules[name]
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            print(f"[PluginManager] Failed to reload {fname}: spec or loader is None")
            return
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
                    instance = obj()
                    self.plugins[name] = instance
                    print(f"[PluginManager] Reloaded plugin: {name}")
        except Exception as e:
            print(f"[PluginManager] Failed to reload {fname}: {e}")

    def reload_all_plugins(self):
        """Hot-reload all plugins."""
        for name in list(self.plugins.keys()):
            self.reload_plugin(name)

    def get_plugin_list(self):
        return [p.info() for p in self.plugins.values()]

    def activate(self, name, app_context=None):
        if name in self.plugins:
            self.plugins[name].activate(app_context)

    def deactivate(self, name):
        if name in self.plugins:
            self.plugins[name].deactivate()

    def get_plugin_widget(self, name, parent=None):
        if name in self.plugins:
            return self.plugins[name].get_widget(parent)
        return None 