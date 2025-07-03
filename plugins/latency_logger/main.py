from PySide6.QtCore import QObject

from plugins.plugin_interface import PluginInterface


class AtlasPlugin(PluginInterface):
    def __init__(self, name: str, version: str, parent: QObject = None):
        super().__init__(name, version, parent)
        self.metadata["name"] = "Latency Logger"
        self.metadata["description"] = "Placeholder for Latency Logger plugin."

    def on_initialize(self) -> bool:
        return True

    def on_shutdown(self) -> None:
        pass
