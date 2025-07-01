from typing import Dict, List, Optional

from modules.agents.task_planner_agent import TaskPlannerAgent
from modules.tasks.task_manager import TaskManager
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.async_task_manager import AsyncTaskManager
from ui.i18n import _


class TasksModule(QWidget):
    """Tasks and Plans management module with cyberpunk styling.

    Attributes:
        task_manager: Task manager instance
        task_planner_agent: Task planner agent instance for autonomous planning
        user_id: Current user ID
        tool_widgets: List of tool UI widgets
        task_list: QListWidget for tasks
        plan_list: QListWidget for plans
        add_task_btn: QPushButton for adding tasks
        del_task_btn: QPushButton for deleting tasks
        create_plan_btn: QPushButton for creating plans
        cancel_plan_btn: QPushButton for canceling plans
        plan_details_text: QTextEdit for displaying plan details
        title: QLabel for module title
    """

    def __init__(
        self,
        task_manager: TaskManager,
        task_planner_agent: TaskPlannerAgent,
        user_id: str,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the tasks and plans module.

        Args:
            task_manager: Task manager instance
            task_planner_agent: Task planner agent instance
            user_id: Current user ID
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("TasksModule")
        self.task_manager = task_manager
        self.task_planner_agent = task_planner_agent
        self.user_id = user_id
        self.tool_widgets: List[QWidget] = []
        self.async_manager = AsyncTaskManager()
        self.async_manager.start()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title = QLabel(_("📋 Tasks & Plans (Cyberpunk)"))
        self.title.setStyleSheet(
            "color: #ff00a0; font-size: 22px; font-weight: bold; letter-spacing: 1px;"
        )
        layout.addWidget(self.title)

        # Create a splitter for tasks and plans
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, stretch=1)

        # Tasks section
        tasks_group = QGroupBox("Tasks")
        tasks_layout = QVBoxLayout(tasks_group)
        self.task_list = QListWidget()
        self.task_list.setDragEnabled(True)
        self.task_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.task_list.setDefaultDropAction(Qt.MoveAction)
        self.task_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.task_list.setStyleSheet(
            "background: #181c20; color: #fff; border: 1px solid #ff00a0; border-radius: 8px; font-size: 15px;"
        )
        tasks_layout.addWidget(self.task_list, stretch=1)

        task_btns = QHBoxLayout()
        self.add_task_btn = QPushButton(_("Add Task"))
        self.add_task_btn.setStyleSheet(
            "background: #ff00a0; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;"
        )
        self.add_task_btn.clicked.connect(self.add_task)
        task_btns.addWidget(self.add_task_btn)
        self.del_task_btn = QPushButton(_("Delete Task"))
        self.del_task_btn.setStyleSheet(
            "background: #23272e; color: #ff00a0; border-radius: 6px; padding: 6px 18px;"
        )
        self.del_task_btn.clicked.connect(self.delete_task)
        task_btns.addWidget(self.del_task_btn)
        tasks_layout.addLayout(task_btns)
        splitter.addWidget(tasks_group)

        # Plans section
        plans_group = QGroupBox("Plans")
        plans_layout = QVBoxLayout(plans_group)
        self.plan_list = QListWidget()
        self.plan_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.plan_list.setStyleSheet(
            "background: #181c20; color: #fff; border: 1px solid #00fff7; border-radius: 8px; font-size: 15px;"
        )
        self.plan_list.currentItemChanged.connect(self.on_plan_selected)
        plans_layout.addWidget(self.plan_list, stretch=1)

        plan_btns = QHBoxLayout()
        self.create_plan_btn = QPushButton(_("Create Plan"))
        self.create_plan_btn.setStyleSheet(
            "background: #00fff7; color: #181c20; font-weight: bold; border-radius: 6px; padding: 6px 18px;"
        )
        self.create_plan_btn.clicked.connect(self.create_plan)
        plan_btns.addWidget(self.create_plan_btn)
        self.cancel_plan_btn = QPushButton(_("Cancel Plan"))
        self.cancel_plan_btn.setStyleSheet(
            "background: #23272e; color: #00fff7; border-radius: 6px; padding: 6px 18px;"
        )
        self.cancel_plan_btn.clicked.connect(self.cancel_plan)
        plan_btns.addWidget(self.cancel_plan_btn)
        plans_layout.addLayout(plan_btns)

        self.plan_details_text = QTextEdit()
        self.plan_details_text.setReadOnly(True)
        self.plan_details_text.setStyleSheet(
            "background: #181c20; color: #fff; border: 1px solid #00fff7; border-radius: 8px; font-size: 14px;"
        )
        plans_layout.addWidget(self.plan_details_text, stretch=1)
        splitter.addWidget(plans_group)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        self.tools_frame = QFrame()
        self.tools_layout = QVBoxLayout(self.tools_frame)
        self.tools_layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.tools_frame)

        self.update_task_list()
        self.update_plan_list()

    def update_ui(self) -> None:
        """Update UI elements with translated text."""
        self.title.setText(
            str(_("📋 Tasks & Plans (Cyberpunk)")) or "📋 Tasks & Plans (Cyberpunk)"
        )
        self.add_task_btn.setText(str(_("Add Task")) or "Add Task")
        self.del_task_btn.setText(str(_("Delete Task")) or "Delete Task")
        self.create_plan_btn.setText(str(_("Create Plan")) or "Create Plan")
        self.cancel_plan_btn.setText(str(_("Cancel Plan")) or "Cancel Plan")

    def update_task_list(self) -> None:
        """Update the task list from the task manager asynchronously."""

        def update_task_list_async():
            try:
                tasks = self.task_manager.get_tasks()
                self.task_list.clear()
                for task in tasks:
                    status = "✓" if task.get("completed", False) else " "
                    item_text = f"[{status}] {task.get('description', 'Unnamed Task')}"
                    self.task_list.addItem(item_text)
            except Exception as e:
                print(f"Error updating task list: {e}")

        self.async_manager.submit_task(update_task_list_async)

    def update_plan_list(self) -> None:
        """Update the plan list from the task planner agent asynchronously."""

        def update_plan_list_async():
            try:
                plans = self.task_planner_agent.get_all_plans()
                self.plan_list.clear()
                for plan_id, plan_details in plans.items():
                    item = QListWidgetItem(plan_details.get("goal", "Unnamed Plan"))
                    item.setData(Qt.UserRole, plan_id)
                    self.plan_list.addItem(item)
            except Exception as e:
                print(f"Error updating plan list: {e}")

        self.async_manager.submit_task(update_plan_list_async)

    def on_plan_selected(self, current, previous) -> None:
        """Handle plan selection change to display plan details.

        Args:
            current: Current selected item
            previous: Previously selected item
        """
        if current:
            plan_id = current.data(Qt.UserRole)
            plan_details = self.task_planner_agent.get_plan_details(plan_id)
            if plan_details:
                self.display_plan_details(plan_details)
        else:
            self.plan_details_text.clear()

    def display_plan_details(self, plan_details: Dict) -> None:
        """Display the details of a selected plan.

        Args:
            plan_details: Dictionary containing plan details
        """
        details = f"<h3>Plan: {plan_details.get('goal', 'Unnamed Plan')}</h3>"
        details += f"<p><b>Status:</b> {plan_details.get('status', 'Unknown')}</p>"
        details += (
            f"<p><b>Progress:</b> {int(plan_details.get('progress', 0.0) * 100)}%</p>"
        )
        details += f"<p><b>Created:</b> {plan_details.get('created_at', 'Unknown')}</p>"
        details += "<h4>Tasks:</h4><ul>"
        for task in plan_details.get("tasks", []):
            status = task.get("status", "pending")
            progress = int(task.get("progress", 0.0) * 100)
            details += f"<li><b>{task.get('description', 'Unnamed Task')}</b>: {status} ({progress}%)</li>"
        details += "</ul>"
        self.plan_details_text.setHtml(details)

    def add_task(self) -> None:
        """Add a new task to the list.

        Opens a dialog to get task name and adds it to the list.
        """
        text, ok = QInputDialog.getText(
            self, str(_("Add Task")) or "Add Task", str(_("Task name:")) or "Task name:"
        )
        if ok and text:
            try:
                self.task_manager.add_task({"description": text, "completed": False})
                self.update_task_list()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{_('Failed to add task:')} {str(e)}",
                )

    def delete_task(self) -> None:
        """Delete the selected task.

        Shows a warning if no task is selected.
        """
        row = self.task_list.currentRow()
        if row >= 0:
            try:
                tasks = self.task_manager.get_tasks()
                if row < len(tasks):
                    task_desc = tasks[row].get("description")
                    self.task_manager.remove_task(task_desc)
                    self.update_task_list()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    f"{str(_('Failed to delete task:')) or 'Failed to delete task:'} {str(e)}",
                )
        else:
            QMessageBox.warning(
                self,
                str(_("Delete Task")) or "Delete Task",
                str(_("Select a task to delete.")) or "Select a task to delete.",
            )

    def create_plan(self) -> None:
        """Create a new plan based on user goal input asynchronously."""
        goal, ok = QInputDialog.getText(
            self,
            str(_("Create Plan")) or "Create Plan",
            str(_("Goal or objective:")) or "Goal or objective:",
        )
        if ok and goal:

            def create_plan_async():
                try:
                    plan_id = self.task_planner_agent.create_task_plan(
                        self.user_id, goal
                    )
                    self.update_plan_list()
                    QMessageBox.information(
                        self,
                        str(_("Plan Created")) or "Plan Created",
                        f"{str(_('Plan created with ID:')) or 'Plan created with ID:'} {plan_id}",
                    )
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        str(_("Error")) or "Error",
                        f"{str(_('Failed to create plan:')) or 'Failed to create plan:'} {str(e)}",
                    )

            self.async_manager.submit_task(create_plan_async)

    def cancel_plan(self) -> None:
        """Cancel the selected plan."""
        selected_item = self.plan_list.currentItem()
        if selected_item:
            plan_id = selected_item.data(Qt.UserRole)
            if self.task_planner_agent.cancel_plan(plan_id):
                self.update_plan_list()
                self.plan_details_text.clear()
                QMessageBox.information(
                    self,
                    str(_("Plan Cancelled")) or "Plan Cancelled",
                    f"{str(_('Plan cancelled:')) or 'Plan cancelled:'} {plan_id}",
                )
            else:
                QMessageBox.warning(
                    self,
                    str(_("Error")) or "Error",
                    str(_("Failed to cancel plan.")) or "Failed to cancel plan.",
                )
        else:
            QMessageBox.warning(
                self,
                str(_("Cancel Plan")) or "Cancel Plan",
                str(_("Select a plan to cancel.")) or "Select a plan to cancel.",
            )

    def search(self, query: str) -> List[Dict[str, str]]:
        """Search for tasks containing the query.

        Args:
            query: Search term

        Returns:
            List of dictionaries with 'label' and 'key' containing matching tasks
        """
        results: List[Dict[str, str]] = []
        for i in range(self.task_list.count()):
            try:
                text = self.task_list.item(i).text()
                if query.lower() in text.lower():
                    results.append({"label": text, "key": text})
            except Exception as e:
                print(f"Error searching task {i}: {e}")
                continue
        return results

    def select_by_key(self, key: str) -> None:
        """Select a task by its key.

        Args:
            key: Task key to select
        """
        for i in range(self.task_list.count()):
            try:
                if self.task_list.item(i).text() == key:
                    self.task_list.setCurrentRow(i)
                    self.task_list.scrollToItem(self.task_list.item(i))
                    break
            except Exception as e:
                print(f"Error selecting task {i}: {e}")
                continue
