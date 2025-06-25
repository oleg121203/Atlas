"""
Onboarding Manager Module for Atlas.
This module manages the onboarding process to simplify initial setup and guide new users through key features.
"""

from PySide6.QtWidgets import QWizard, QWizardPage, QLabel, QVBoxLayout, QPushButton, QLineEdit, QCheckBox
from PySide6.QtCore import Qt
from analytics.onboarding_analytics import OnboardingAnalytics

class OnboardingManager(QWizard):
    """
    A wizard-based class to guide new users through the Atlas onboarding process.
    """
    def __init__(self, parent=None):
        """
        Initialize the OnboardingManager wizard with predefined pages.
        
        Args:
            parent: Parent widget, if any.
        """
        super().__init__(parent)
        self.setWindowTitle("Atlas Onboarding Guide")
        self.setWizardStyle(QWizard.ModernStyle)
        self.analytics = OnboardingAnalytics()
        self.analytics.start_session("new_user")  # In a real app, use unique user ID
        
        # Add pages to the wizard
        self.addPage(WelcomePage(self))
        self.addPage(AccountSetupPage(self))
        self.addPage(FeatureTourPage(self))
        self.addPage(CustomizationPage(self))
        self.addPage(FinalPage(self))
        
        # Track the start of onboarding
        self.analytics.track_step("Welcome", completed=True)
        
        # Connect signals
        self.accepted.connect(self.on_finish)
        self.rejected.connect(self.on_cancel)
        self.currentIdChanged.connect(self.on_page_change)

    def on_finish(self):
        """
        Handle the completion of the onboarding process.
        """
        print("Onboarding completed. Saving user preferences.")
        self.analytics.end_session(completed_onboarding=True)
        # Save user data and preferences here
        # e.g., self.save_user_data()

    def on_cancel(self):
        """
        Handle cancellation of the onboarding process.
        """
        print("Onboarding cancelled. Using default settings.")
        self.analytics.end_session(completed_onboarding=False)
        # Optionally, set default settings or prompt for confirmation

    def on_page_change(self, page_id):
        """
        Track when users move to a new page in the onboarding process.
        
        Args:
            page_id: ID of the current page.
        """
        page_titles = {
            0: "Welcome",
            1: "Account Setup",
            2: "Feature Tour",
            3: "Customization",
            4: "All Set"
        }
        if page_id in page_titles:
            self.analytics.track_step(page_titles[page_id], completed=True)
        print(f"Moved to page: {page_titles.get(page_id, 'Unknown')}")

class WelcomePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Atlas")
        self.setSubTitle("Your journey to productivity starts here!")
        
        layout = QVBoxLayout()
        welcome_label = QLabel(
            "Atlas is your personal productivity assistant. "
            "This guide will help you set up your account and explore key features. "
            "Click Next to begin."
        )
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        self.setLayout(layout)

class AccountSetupPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Account Setup")
        self.setSubTitle("Let\'s get to know you.")
        
        layout = QVBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        sync_label = QLabel("Enable Cloud Sync:")
        self.sync_checkbox = QCheckBox()
        
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(sync_label)
        layout.addWidget(self.sync_checkbox)
        self.setLayout(layout)
        
        self.registerField("name*", self.name_input)
        self.registerField("email", self.email_input)
        self.registerField("sync", self.sync_checkbox)

    def validatePage(self):
        name = self.field("name")
        if not name:
            return False
        return True

class FeatureTourPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Feature Tour")
        self.setSubTitle("Discover what Atlas can do for you.")
        
        layout = QVBoxLayout()
        features_label = QLabel(
            "- Task Management: Organize tasks with ease.\n"
            "- AI Suggestions: Get personalized task recommendations.\n"
            "- Customization: Tailor Atlas to your preferences.\n"
            "- Collaboration: Work seamlessly with your team."
        )
        features_label.setWordWrap(True)
        play_button = QPushButton("Play Interactive Tutorial")
        play_button.clicked.connect(self.play_tutorial)
        
        layout.addWidget(features_label)
        layout.addWidget(play_button)
        self.setLayout(layout)

    def play_tutorial(self):
        print("Starting interactive tutorial...")
        # Placeholder for launching an interactive tutorial or video

class CustomizationPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Customization")
        self.setSubTitle("Make Atlas your own.")
        
        layout = QVBoxLayout()
        theme_label = QLabel("Select Theme:")
        self.dark_theme = QCheckBox("Dark Mode")
        notifications_label = QLabel("Enable Notifications:")
        self.notifications = QCheckBox()
        
        layout.addWidget(theme_label)
        layout.addWidget(self.dark_theme)
        layout.addWidget(notifications_label)
        layout.addWidget(self.notifications)
        self.setLayout(layout)
        
        self.registerField("darkTheme", self.dark_theme)
        self.registerField("notifications", self.notifications)

class FinalPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("All Set!")
        self.setSubTitle("You\'re ready to boost your productivity with Atlas.")
        
        layout = QVBoxLayout()
        final_label = QLabel(
            "You\'ve completed the setup. Click Finish to start using Atlas. "
            "You can always revisit these settings in the Preferences menu."
        )
        final_label.setWordWrap(True)
        layout.addWidget(final_label)
        self.setLayout(layout)

# Example usage
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    wizard = OnboardingManager()
    wizard.show()
    sys.exit(app.exec())
