from plugins.base import PluginBase
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
import random

class TaskGeneratorPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.widget = None

    def get_widget(self, parent=None):
        if self.widget is None:
            self.widget = QWidget(parent)
            layout = QVBoxLayout(self.widget)
            self.label = QLabel("Click to generate a task")
            layout.addWidget(self.label)
            btn = QPushButton("Generate Task")
            btn.clicked.connect(self.generate_task)
            layout.addWidget(btn)
        return self.widget

    def generate_task(self):
        tasks = [
            "Write a report about Atlas",
            "Fix bug in agent communication",
            "Refactor plugin system",
            "Test LLM integration",
            "Update documentation",
            "Optimize memory usage",
            "Design new UI panel",
            "Implement drag&drop for tasks",
        ]
        self.label.setText(random.choice(tasks))

    def info(self):
        return {
            "name": "TaskGeneratorPlugin",
            "description": "Generates random tasks for demo purposes.",
            "active": self.active
        } 