"""
Interactive Onboarding Tutorial Module for Atlas.
This module provides an interactive tutorial to guide new users through key features of Atlas.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class OnboardingTutorial(QDialog):
    """
    A dialog-based interactive tutorial to guide users through Atlas features.
    """

    def __init__(self, parent=None):
        """
        Initialize the OnboardingTutorial dialog with a series of tutorial steps.

        Args:
            parent: Parent widget, if any.
        """
        super().__init__(parent)
        self.setWindowTitle("Atlas Interactive Tutorial")
        self.setMinimumSize(QSize(600, 400))
        self.current_step = 0
        self.steps = self._define_steps()
        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface for the tutorial dialog.
        """
        layout = QVBoxLayout(self)

        # Title and description area
        self.title_label = QLabel("", self)
        self.title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-bottom: 10px;"
        )
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.description_label = QLabel("", self)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.description_label)

        # Visual demo area (placeholder for animations or images)
        self.demo_area = QFrame(self)
        self.demo_area.setFrameShape(QFrame.Box)
        self.demo_area.setMinimumHeight(200)
        self.demo_area.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        layout.addWidget(self.demo_area)

        # Navigation buttons
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous", self)
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)
        btn_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next", self)
        self.next_btn.clicked.connect(self.next_step)
        btn_layout.addWidget(self.next_btn)

        self.finish_btn = QPushButton("Finish", self)
        self.finish_btn.clicked.connect(self.accept)
        self.finish_btn.setVisible(False)
        btn_layout.addWidget(self.finish_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.update_content()

    def _define_steps(self):
        """
        Define the steps of the tutorial with titles and descriptions.

        Returns:
            list: List of dictionaries containing tutorial step data.
        """
        return [
            {
                "title": "Welcome to Atlas",
                "description": "Atlas helps you manage tasks efficiently. Let's explore how to create your first task.",
            },
            {
                "title": "Creating a Task",
                "description": "Click the '+' button to add a new task. Enter a title, description, and due date. Try it now!",
            },
            {
                "title": "Using AI Suggestions",
                "description": "Atlas suggests tasks based on your habits. Click 'AI Suggest' to see personalized recommendations.",
            },
            {
                "title": "Organizing with Lists",
                "description": "Group tasks into lists for better organization. Create a list by clicking 'New List'.",
            },
            {
                "title": "Collaboration Features",
                "description": "Share tasks or lists with your team. Click 'Share' to invite collaborators.",
            },
            {
                "title": "Customization Options",
                "description": "Personalize Atlas with themes and layouts. Visit 'Settings' to customize your experience.",
            },
            {
                "title": "You're Ready!",
                "description": "You've learned the basics of Atlas. Start using it to boost your productivity!",
            },
        ]

    def update_content(self):
        """
        Update the dialog content based on the current step.
        """
        step = self.steps[self.current_step]
        self.title_label.setText(step["title"])
        self.description_label.setText(step["description"])

        # Update demo area color or content for visual feedback (placeholder)
        colors = [
            "#f0f0f0",
            "#e6f2ff",
            "#fff0e6",
            "#e6ffe6",
            "#ffe6f2",
            "#ffffe6",
            "#e6e6ff",
        ]
        self.demo_area.setStyleSheet(
            f"background-color: {colors[self.current_step % len(colors)]}; border: 1px solid #ccc;"
        )

        # Update button states
        self.prev_btn.setEnabled(self.current_step > 0)
        self.next_btn.setVisible(self.current_step < len(self.steps) - 1)
        self.finish_btn.setVisible(self.current_step == len(self.steps) - 1)

    def next_step(self):
        """
        Move to the next step in the tutorial.
        """
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_content()

    def previous_step(self):
        """
        Move to the previous step in the tutorial.
        """
        if self.current_step > 0:
            self.current_step -= 1
            self.update_content()


# Example usage
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    tutorial = OnboardingTutorial()
    tutorial.show()
    sys.exit(app.exec())
