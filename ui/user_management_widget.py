"""
User Management widget for the Atlas application.

This module provides the UI component for user management, including
role assignment and permission viewing with RBAC integration.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QComboBox, QLabel, QMessageBox
from PySide6.QtCore import Qt

from ui.input_validation import validate_ui_input, sanitize_ui_input
from security.rbac import Role, get_rbac_manager
from core.logging import get_logger

logger = get_logger("UserManagementWidget")

class UserManagementWidget(QWidget):
    """User management interface widget for Atlas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rbac_manager = get_rbac_manager()
        self.init_ui()
        logger.info("User management widget initialized")
    
    def init_ui(self) -> None:
        """Initialize UI components for the user management widget."""
        layout = QVBoxLayout(self)
        
        # User list
        user_list_label = QLabel("Users:")
        layout.addWidget(user_list_label)
        self.user_list = QListWidget()
        self.refresh_user_list()
        self.user_list.itemClicked.connect(self.display_user_role)
        layout.addWidget(self.user_list)
        
        # Add user section
        add_user_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username...")
        add_user_layout.addWidget(username_label)
        add_user_layout.addWidget(self.username_input)
        
        role_label = QLabel("Role:")
        self.role_combo = QComboBox()
        self.role_combo.addItems([role.value for role in Role])
        add_user_layout.addWidget(role_label)
        add_user_layout.addWidget(self.role_combo)
        
        add_button = QPushButton("Add/Update User")
        add_button.clicked.connect(self.add_or_update_user)
        add_user_layout.addWidget(add_button)
        layout.addLayout(add_user_layout)
        
        # Remove user button
        remove_button = QPushButton("Remove Selected User")
        remove_button.clicked.connect(self.remove_user)
        layout.addWidget(remove_button)
        
        # User role display
        role_display_label = QLabel("Selected User Role:")
        layout.addWidget(role_display_label)
        self.role_display = QLabel("Select a user to view role")
        layout.addWidget(self.role_display)
        
        # Permissions display
        perms_label = QLabel("Permissions for Selected User:")
        layout.addWidget(perms_label)
        self.perms_list = QListWidget()
        layout.addWidget(self.perms_list)
    
    def refresh_user_list(self) -> None:
        """Refresh the list of users from RBAC manager."""
        self.user_list.clear()
        for username in self.rbac_manager.user_roles.keys():
            self.user_list.addItem(QListWidgetItem(username))
        logger.debug("User list refreshed")
    
    def add_or_update_user(self) -> None:
        """Handle adding or updating a user with a role."""
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Invalid Input", "Username cannot be empty")
            return
        
        # Validate input
        is_valid, error_msg = validate_ui_input(username, "username", "Username")
        if not is_valid:
            logger.warning("Invalid username input: %s", error_msg)
            QMessageBox.warning(self, "Invalid Input", error_msg)
            return
        
        # Sanitize input
        sanitized_username = sanitize_ui_input(username)
        logger.debug("Username sanitized, original: %s, sanitized: %s", username, sanitized_username)
        
        # Get selected role
        role_str = self.role_combo.currentText()
        role = Role(role_str)
        
        # Assign role
        self.rbac_manager.assign_user_role(sanitized_username, role)
        logger.info("User %s added/updated with role %s", sanitized_username, role_str)
        
        # Show success and refresh UI
        QMessageBox.information(self, "Success", f"User {sanitized_username} added/updated with role {role_str}")
        self.username_input.clear()
        self.refresh_user_list()
        
        # If this was the added user, update the display
        if self.user_list.currentItem() and self.user_list.currentItem().text() == sanitized_username:
            self.display_user_role(self.user_list.currentItem())
    
    def remove_user(self) -> None:
        """Handle removing a selected user."""
        selected_item = self.user_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a user to remove")
            return
        
        username = selected_item.text()
        self.rbac_manager.remove_user_role(username)
        logger.info("User %s removed from RBAC", username)
        
        QMessageBox.information(self, "Success", f"User {username} removed")
        self.refresh_user_list()
        self.role_display.setText("Select a user to view role")
        self.perms_list.clear()
    
    def display_user_role(self, item: QListWidgetItem) -> None:
        """
        Display the role and permissions of the selected user.
        
        Args:
            item: Selected user item
        """
        username = item.text()
        role = self.rbac_manager.get_user_role(username)
        if role:
            self.role_display.setText(f"Role: {role.value}")
            
            # Display permissions
            permissions = self.rbac_manager.get_user_permissions(username)
            self.perms_list.clear()
            for perm in sorted(permissions, key=lambda p: p.value):
                self.perms_list.addItem(QListWidgetItem(perm.value))
            logger.debug("Displayed role and permissions for user %s", username)
        else:
            self.role_display.setText("Role: None (Not assigned)")
            self.perms_list.clear()
            logger.warning("No role assigned to selected user %s", username)
