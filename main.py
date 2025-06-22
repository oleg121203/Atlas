#!/usr/bin/env python3
"""
Atlas: Autonomous Computer Agent

Entry point for the application. Initializes the CustomTkinter GUI and
loads configuration.
"""

import platform
import sys

#Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()  #Load .env file variables
except ImportError:
    pass  #dotenv is optional

#Import platform utilities
from utils.platform_utils import (
    IS_HEADLESS,
    IS_LINUX,
    IS_MACOS,
    IS_WINDOWS,
    configure_for_platform,
    get_platform_info,
)

#Configure for current platform
configure_for_platform()

import argparse
import inspect
import json
import logging
import multiprocessing
import os
import threading
import tkinter as tk
from datetime import datetime
from typing import Any, Dict, Optional

import customtkinter as ctk
from customtkinter import CTkImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from agents.agent_manager import AgentManager
from agents.chat_context_manager import ChatContextManager, ChatMode
from agents.chat_translation_manager import ChatTranslationManager
from agents.creator_authentication import CreatorAuthentication, CreatorIdentityLevel
from agents.encrypted_creator_protocols import EncryptedCreatorProtocols
from agents.enhanced_deputy_agent import EnhancedDeputyAgent
from agents.enhanced_memory_manager import (
    EnhancedMemoryManager,
    MemoryScope,
    MemoryType,
)
from agents.enhanced_security_agent import EnhancedSecurityAgent
from agents.master_agent import MasterAgent
from agents.task_manager import TaskManager, TaskPriority, TaskStatus
from agents.token_tracker import TokenTracker
from intelligence.context_awareness_engine import ContextAwarenessEngine
from monitoring.metrics_manager import metrics_manager
from plugin_manager import PluginManager
from tools.code_reader_tool import CodeReaderTool
from tools.screenshot_tool import capture_screen
from ui.chat_history_view import ChatHistoryView
from ui.context_menu import enable_formatting_context_menu
from ui.enhanced_plugin_manager import EnhancedPluginManagerWindow
from ui.enhanced_settings import EnhancedSettingsView
from ui.goal_history import GoalHistoryManager, GoalHistoryWindow
from ui.plan_view import PlanView
from ui.status_panel import StatusPanel
from ui.tool_management_view import ToolManagementView
from utils.config_manager import ConfigManager
from utils.gui_logger import GuiLogger
from utils.llm_manager import LLMManager
from utils.logger import add_handler, get_logger

#Platform-specific imports
if IS_MACOS:
    from utils.macos_utils import (
        check_macos_permissions,
        configure_macos_gui,
        setup_macos_dock_icon,
    )


class AtlasApp(ctk.CTk):
    """Primary CustomTkinter application window."""

    def __init__(self):
        super().__init__()

        #Verification протоколів безпеки (скритий процес)
        if not self._verify_security_protocols():
            sys.exit(1)

        self.logger = get_logger()
        self.title("Atlas – Autonomous Computer Agent")
        self.geometry("1200x800")

        #Platform-specific setup
        if IS_MACOS:
            configure_macos_gui()
            #Set up dock icon if available
            icon_path = setup_macos_dock_icon()
            if icon_path:
                try:
                    self.iconbitmap(icon_path)
                except Exception as e:
                    self.logger.debug(f"Could not set icon: {e}")

        self._setup_theme()

        #Initialize managers in the correct order
        self.config_manager = ConfigManager()
        self.token_tracker = TokenTracker()
        self.llm_manager = LLMManager(token_tracker=self.token_tracker, config_manager=self.config_manager)
        self.memory_manager = EnhancedMemoryManager(llm_manager=self.llm_manager, config_manager=self.config_manager)
        self.agent_manager = AgentManager(llm_manager=self.llm_manager, memory_manager=self.memory_manager)
        self.plugin_manager = PluginManager(self.agent_manager)
        #Set plugin manager reference to avoid circular dependency

        #Initialize the chat context manager
        self.chat_context_manager = ChatContextManager(memory_manager=self.memory_manager)

        #Initialize the chat translation manager (without LLM manager initially)
        self.chat_translation_manager = ChatTranslationManager()

        #Initialize Creator Authentication System
        self.creator_auth = CreatorAuthentication(config_manager=self.config_manager)

        #Initialize TaskManager for multi-goal support
        self.task_manager = TaskManager(
            max_concurrent_tasks=3,
            llm_manager=self.llm_manager,
            agent_manager=self.agent_manager,
            memory_db_path=self.config_manager.get_memory_db_path(),
        )

        #Initialize the code reader tool for Help mode
        self.code_reader = CodeReaderTool()

        self.agent_manager.set_plugin_manager(self.plugin_manager)

        #Initialize Goal History Manager
        self.goal_history_manager = GoalHistoryManager()

        #Create the ChatHistoryView early so it can be used as a callback
        self.chat_history_view = ChatHistoryView(master=self)

        #Initialize Master Agent
        self.last_goal = None
        self.current_plan = None
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.context_awareness_engine = ContextAwarenessEngine(project_root=project_root)

        self.master_agent = MasterAgent(
            agent_manager=self.agent_manager,
            llm_manager=self.llm_manager,
            memory_manager=self.memory_manager,
            context_awareness_engine=self.context_awareness_engine,
            status_callback=self._handle_agent_status,
            creator_auth=self.creator_auth,
        )

        #Set the LLM manager for translation after master_agent is created
        if hasattr(self, "chat_translation_manager") and self.llm_manager:
            self.chat_translation_manager.set_llm_manager(self.llm_manager)

        #Discover plugins after all managers are ready
        self.plugin_manager.discover_plugins(self.llm_manager, atlas_app=self)
        self._log_loaded_plugins()

        #Initialize enhanced agents
        self.deputy_agent = EnhancedDeputyAgent(
            llm_manager=self.llm_manager,
            agent_manager=self.agent_manager,
        )

        #Set up communication with the Enhanced Security Agent
        parent_conn, child_conn = multiprocessing.Pipe()
        self.security_agent_conn = parent_conn
        self.security_agent = EnhancedSecurityAgent(child_conn, self.config_manager)

        self.agent_cards = []
        self.run_button = None
        self.progress_bar = None

        #Token labels - initialized to None
        self.prompt_tokens_label = None
        self.completion_tokens_label = None
        self.total_tokens_label = None

        #Notification settings variables
        self.notification_email_var = ctk.BooleanVar()
        self.notification_telegram_var = ctk.BooleanVar()
        self.notification_sms_var = ctk.BooleanVar()

        #API Key variables
        self.openai_api_key_var = ctk.StringVar()
        self.anthropic_api_key_var = ctk.StringVar()
        self.gemini_api_key_var = ctk.StringVar()
        self.groq_api_key_var = ctk.StringVar()
        self.mistral_api_key_var = ctk.StringVar()

        #Plugin enabled/disabled state variables
        self.plugin_enabled_vars: Dict[str, ctk.BooleanVar] = {}

        #Load initial settings into memory
        self._load_settings()

        #Build the main interface
        self._create_widgets()

        #Apply loaded settings to the UI
        self._apply_settings_to_ui()

        #Load the rest of the app state
        self._load_app_state()

        #Start background agents and processes
        self.deputy_agent.start()
        self.security_agent.start()

        #Set up graceful shutdown
        self.protocol("WM_DELETE_WINDOW", self._on_close)



    def _handle_agent_status(self, message: Dict[str, Any]):
        """Routes status messages from the agent to the correct UI component."""
        msg_type = message.get("type")
        data = message.get("data")
        content = message.get("content")

        #Ensure UI updates happen on the main thread
        def _update_ui():
            #Update status panel if available
            if hasattr(self, "status_panel"):
                self.status_panel.handle_agent_message(message)

            if msg_type == "plan":
                self.current_plan = data
                self.plan_view.display_plan(data)
                self.chat_history_view.add_message("agent", f"Generated a new plan for goal: {self.last_goal}")
            elif msg_type == "step_start":
                self.plan_view.update_step_status(data["index"], "start", data)
            elif msg_type == "step_end":
                self.plan_view.update_step_status(data["index"], "end", data)
            elif msg_type == "request_clarification":
                self.chat_history_view.add_message(message["role"], message["content"])
                self._prompt_for_clarification(content)
            elif msg_type == "request_feedback":
                self.chat_history_view.add_message(message["role"], message["content"])
                self._prompt_for_feedback(content)
            elif msg_type == "success":
                self.chat_history_view.add_message(message["role"], message["content"])
                #Add to goal history
                if self.last_goal:
                    self.goal_history_manager.add_goal(
                        self.last_goal,
                        "Completed",
                        execution_time=data.get("execution_time"),
                        steps_completed=data.get("steps_completed"),
                        total_steps=data.get("total_steps"),
                    )
                self.feedback_frame.grid() #Show feedback buttons
            elif msg_type == "error" or msg_type == "failure":
                #Add failed goal to history
                if self.last_goal:
                    self.goal_history_manager.add_goal(
                        self.last_goal,
                        "Failed",
                        error_message=content,
                        steps_completed=data.get("steps_completed"),
                        total_steps=data.get("total_steps"),
                    )
                self.chat_history_view.add_message(message["role"], message["content"])
            else:
                self.chat_history_view.add_message(message["role"], message["content"])

        self.after(0, _update_ui)

    def _prompt_for_feedback(self, prompt_text: str):
        """Creates and shows the feedback dialog, then sends the result to the agent."""
        dialog = ctk.CTkInputDialog(
            text=prompt_text + "\n\nOptions: 'skip', 'abort', or provide new instructions.",
            title="Agent Needs Guidance",
        )
        feedback = dialog.get_input()

        if feedback:
            self.master_agent.continue_with_feedback(feedback)
        else:
            #If the user closes the dialog or enters nothing, treat it as an abort.
            self.master_agent.continue_with_feedback("abort")

    def _prompt_for_clarification(self, question: str):
        """Creates a dialog to get clarification from the user."""
        self.logger.info(f"Prompting user for clarification: {question}")

        #Translate question to Ukrainian for user
        translated_question = question
        try:
            if hasattr(self, "chat_translation_manager"):
                translated_question = self.chat_translation_manager.process_outgoing_response(question)
                if translated_question != question:
                    self.logger.info(f"Translated clarification question to user language: {translated_question}")
        except Exception as e:
            self.logger.warning(f"Failed to translate clarification question: {e}")

        dialog = ctk.CTkInputDialog(
            text=translated_question,
            title="Agent Needs Clarification" if translated_question == question else "Агент потребує уточнення",
        )
        clarification = dialog.get_input()

        if clarification:
            self.logger.info(f"User provided clarification: {clarification}")

            #Translate clarification back to English for the agent
            processed_clarification = clarification
            try:
                if hasattr(self, "chat_translation_manager"):
                    processed_clarification, _ = self.chat_translation_manager.process_incoming_message(clarification)
                    if processed_clarification != clarification:
                        self.logger.info(f"Translated user clarification for agent: {processed_clarification}")
            except Exception as e:
                self.logger.warning(f"Failed to translate clarification response: {e}")

            #Send the clarification back to the agent, which will unpause it
            self.master_agent.provide_clarification(processed_clarification)
        else:
            #If the user cancels or provides no input, stop the current run.
            self.logger.warning("User cancelled clarification. Stopping the current goal.")
            self._on_stop()

    def _verify_security_protocols(self) -> bool:
        """
        Скрита verification протоколів безпеки при запуску.
        Якщо протоколи не знайдені або недійсні, програма не запускається.
        """
        try:
            #Створюємо екземпляр протоколів
            protocols = EncryptedCreatorProtocols()

            #Перевіряємо доступність протоколів
            if not protocols.verify_protocols_integrity():
                #Протоколи пошкоджені або відсутні
                import tkinter as tk
                from tkinter import messagebox

                root = tk.Tk()
                root.withdraw()  #Приховуємо головне вікно

                messagebox.showerror(
                    "Помилка ініціалізації",
                    "Не шукайте Бога на небі, шукайте в серці своєму, в собі !",
                )

                root.destroy()
                return False

            #Протоколи успішно перевірені
            return True

        except Exception:
            #Якщо сталася помилка при перевірці
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()

            messagebox.showerror(
                "Помилка ініціалізації",
                "Не шукайте Бога на небі, шукайте в серці своєму, в собі !",
            )

            root.destroy()
            return False

    def _setup_theme(self):
        """Setup appearance and color theme."""
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

    def _create_widgets(self) -> None:
        """Create and configure the main GUI layout and widgets."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        tabview = ctk.CTkTabview(self, anchor="nw")
        tabview.grid(row=0, column=0, sticky="nsew")

        #Configure tabs
        self._create_chat_tab(tabview.add("Chat"))  #Interactive chat interface
        self._create_master_agent_tab(tabview.add("Master Agent"))
        self._create_tasks_tab(tabview.add("Tasks"))  #Multi-task management
        self._create_status_tab(tabview.add("Status"))  #New enhanced status tab
        self._create_agents_tab(tabview.add("Agents"))
        self._create_tools_tab(tabview.add("Tools"))
        self._create_logs_tab(tabview.add("Logs & History"))
        self._create_memory_tab(tabview.add("Memory Viewer"))
        self._create_performance_tab(tabview.add("Performance"))
        self._create_enhanced_settings_tab(tabview.add("Settings"))  #Enhanced settings
        self._create_security_tab(tabview.add("Security"))

        #--- Feedback Frame ---
        self.feedback_frame = ctk.CTkFrame(self)
        self.feedback_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        feedback_label = ctk.CTkLabel(self.feedback_frame, text="Rate the last run:")
        feedback_label.pack(side="left", padx=(10, 5))
        self.good_button = ctk.CTkButton(self.feedback_frame, text="👍 Good", command=lambda: self._handle_feedback(True))
        self.good_button.pack(side="left", padx=5)
        self.bad_button = ctk.CTkButton(self.feedback_frame, text="👎 Bad", command=lambda: self._handle_feedback(False))
        self.bad_button.pack(side="left", padx=5)
        self.feedback_frame.grid_remove()  #Initially hidden

    def _create_tools_tab(self, tab):
        """Creates the UI for the Tools tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tool_management_view = ToolManagementView(tab, self.agent_manager)
        tool_management_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _clear_goal_text(self):
        """Clears the content of the goal input textbox."""
        self.goal_text.delete("1.0", ctk.END)

    def _create_master_agent_tab(self, tab):
        """Create the widgets for the Master Agent tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(4, weight=1) #Let the preview area expand

        #--- Goal Input Frame ---
        goal_frame = ctk.CTkFrame(tab, fg_color="transparent")
        goal_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        goal_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(goal_frame, text="Goal").pack(side="left")

        #Goal history and plugin manager buttons
        history_button = ctk.CTkButton(goal_frame, text="Goal History", width=100, command=self._open_goal_history)
        history_button.pack(side="right", padx=(5, 0))

        plugins_button = ctk.CTkButton(goal_frame, text="Plugin Manager", width=120, command=self._open_enhanced_plugin_manager)
        plugins_button.pack(side="right", padx=(5, 0))

        clear_button = ctk.CTkButton(goal_frame, text="Clear", width=60, command=self._clear_goal_text)
        clear_button.pack(side="right", padx=(5, 0))

        #--- Goal Textbox ---
        self.goal_text = ctk.CTkTextbox(tab, height=120)
        self.goal_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        #--- Controls Frame --- #
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)

        #Master prompt
        ctk.CTkLabel(controls_frame, text="Master Prompt").grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 0), sticky="w")
        self.prompt_text = ctk.CTkTextbox(controls_frame, height=80)
        self.prompt_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        #Execution options
        options_frame = ctk.CTkFrame(controls_frame)
        options_frame.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.goal_list_var = ctk.BooleanVar()
        self.cyclic_var = ctk.BooleanVar()
        ctk.CTkCheckBox(options_frame, text="Goal List", variable=self.goal_list_var).pack(side="left", padx=5)
        ctk.CTkCheckBox(options_frame, text="Cyclic Mode", variable=self.cyclic_var).pack(side="left", padx=5)

        #Control buttons
        btn_frame = ctk.CTkFrame(controls_frame)
        btn_frame.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.run_button = ctk.CTkButton(btn_frame, text="Run", command=self._on_run)
        self.run_button.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Pause", command=self._on_pause).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Stop", command=self._on_stop).pack(side="left", padx=5)

        #--- Progress Bar --- #
        self.progress_bar = ctk.CTkProgressBar(tab, mode="indeterminate")

        #--- Plan View --- #
        self.plan_view = PlanView(tab)
        self.plan_view.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        #--- Live Screenshot Preview --- #
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(preview_frame, text="Preview loading...")
        self.preview_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self._update_preview()

    def _create_tasks_tab(self, tab):
        """Create the widgets for the Tasks Management tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)  #Let the tasks list expand

        #--- New Task Frame ---
        task_input_frame = ctk.CTkFrame(tab)
        task_input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        task_input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(task_input_frame, text="New Goal:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.new_task_entry = ctk.CTkEntry(task_input_frame, placeholder_text="Enter a goal for parallel execution...")
        self.new_task_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        #Priority selection
        ctk.CTkLabel(task_input_frame, text="Priority:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.task_priority_var = ctk.StringVar(value="Normal")
        priority_menu = ctk.CTkOptionMenu(task_input_frame, variable=self.task_priority_var,
                                         values=["Low", "Normal", "High", "Urgent"])
        priority_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        #Buttons
        btn_frame = ctk.CTkFrame(task_input_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.create_task_btn = ctk.CTkButton(btn_frame, text="🚀 Create Task", command=self._create_new_task)
        self.create_task_btn.pack(side="left", padx=5)

        self.start_task_manager_btn = ctk.CTkButton(btn_frame, text="▶️ Start TaskManager", command=self._start_task_manager)
        self.start_task_manager_btn.pack(side="left", padx=5)

        self.stop_task_manager_btn = ctk.CTkButton(btn_frame, text="⏹️ Stop TaskManager", command=self._stop_task_manager)
        self.stop_task_manager_btn.pack(side="left", padx=5)

        #--- Task Statistics Frame ---
        stats_frame = ctk.CTkFrame(tab)
        stats_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        #Statistics labels
        self.active_tasks_label = ctk.CTkLabel(stats_frame, text="Active Tasks: 0")
        self.active_tasks_label.grid(row=0, column=0, padx=10, pady=5)

        self.completed_tasks_label = ctk.CTkLabel(stats_frame, text="Completed: 0")
        self.completed_tasks_label.grid(row=0, column=1, padx=10, pady=5)

        self.api_usage_label = ctk.CTkLabel(stats_frame, text="API Usage: 0/60")
        self.api_usage_label.grid(row=0, column=2, padx=10, pady=5)

        #--- Tasks List Frame ---
        tasks_frame = ctk.CTkFrame(tab)
        tasks_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tasks_frame.grid_columnconfigure(0, weight=1)
        tasks_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tasks_frame, text="Running Tasks", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10)

        #Scrollable frame for tasks
        self.tasks_scrollable = ctk.CTkScrollableFrame(tasks_frame)
        self.tasks_scrollable.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tasks_scrollable.grid_columnconfigure(0, weight=1)

        #Initialize task display variables
        self.task_widgets = {}

        #Start periodic updates
        self._update_task_display()

    def _create_new_task(self):
        """Create a new task from the input field."""
        goal = self.new_task_entry.get().strip()
        if not goal:
            self.logger.warning("Cannot create task: no goal specified")
            return

        #Map priority string to enum
        priority_map = {
            "Low": TaskPriority.LOW,
            "Normal": TaskPriority.NORMAL,
            "High": TaskPriority.HIGH,
            "Urgent": TaskPriority.URGENT,
        }
        priority = priority_map.get(self.task_priority_var.get(), TaskPriority.NORMAL)

        try:
            task_id = self.task_manager.create_task(
                goal=goal,
                priority=priority,
                status_callback=self._task_status_callback,
                progress_callback=self._task_progress_callback,
            )

            self.logger.info(f"Created task {task_id}: {goal}")
            self.new_task_entry.delete(0, "end")

            #Update display
            self._update_task_display()

        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")

    def _start_task_manager(self):
        """Start the TaskManager."""
        try:
            self.task_manager.start()
            self.logger.info("TaskManager started")
            self.start_task_manager_btn.configure(state="disabled")
            self.stop_task_manager_btn.configure(state="normal")
        except Exception as e:
            self.logger.error(f"Failed to start TaskManager: {e}")

    def _stop_task_manager(self):
        """Stop the TaskManager."""
        try:
            self.task_manager.stop()
            self.logger.info("TaskManager stopped")
            self.start_task_manager_btn.configure(state="normal")
            self.stop_task_manager_btn.configure(state="disabled")
        except Exception as e:
            self.logger.error(f"Failed to stop TaskManager: {e}")

    def _task_status_callback(self, task_id: str, status: str, details: Optional[Dict[Any, Any]] = None) -> None:
        """Callback for task status updates."""
        self.logger.info(f"Task {task_id} status: {status}")
        if details:
            self.logger.debug(f"Task {task_id} details: {details}")

        #Update UI in main thread
        self.after(0, self._update_task_display)

    def _task_progress_callback(self, task_id: str, progress: float, message: str = ""):
        """Callback for task progress updates."""
        self.logger.debug(f"Task {task_id} progress: {progress:.1%} - {message}")

        #Update UI in main thread
        self.after(0, self._update_task_display)

    def _update_task_display(self):
        """Update the task display in the UI."""
        try:
            #Clear existing widgets
            for widget in self.task_widgets.values():
                widget.destroy()
            self.task_widgets.clear()

            #Get current tasks
            tasks = self.task_manager.tasks
            running_tasks = self.task_manager.running_tasks

            #Update statistics
            active_count = len([t for t in tasks.values() if t.status in [TaskStatus.RUNNING, TaskStatus.PENDING]])
            completed_count = len([t for t in tasks.values() if t.status == TaskStatus.COMPLETED])

            self.active_tasks_label.configure(text=f"Active Tasks: {active_count}")
            self.completed_tasks_label.configure(text=f"Completed: {completed_count}")

            #Get API usage
            api_stats = self.task_manager.api_resource_manager.get_provider_stats()
            openai_usage = api_stats.get("openai", {}).get("current_usage", 0)
            openai_limit = api_stats.get("openai", {}).get("limit", 60)
            self.api_usage_label.configure(text=f"API Usage: {openai_usage}/{openai_limit}")

            #Display each task
            for i, (task_id, task) in enumerate(tasks.items()):
                task_frame = ctk.CTkFrame(self.tasks_scrollable)
                task_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
                task_frame.grid_columnconfigure(1, weight=1)

                #Status indicator
                status_color = {
                    TaskStatus.PENDING: "orange",
                    TaskStatus.RUNNING: "green",
                    TaskStatus.COMPLETED: "blue",
                    TaskStatus.FAILED: "red",
                    TaskStatus.CANCELLED: "gray",
                    TaskStatus.PAUSED: "yellow",
                }.get(task.status, "gray")

                status_label = ctk.CTkLabel(task_frame, text="●", text_color=status_color, font=("Arial", 20))
                status_label.grid(row=0, column=0, padx=5, pady=5)

                #Task info
                info_text = f"{task_id}: {task.goal[:50]}..."
                if len(task.goal) > 50:
                    info_text += f"\nStatus: {task.status.value.upper()}"
                if task.created_at:
                    info_text += f"\nCreated: {task.created_at.strftime('%H:%M:%S')}"

                info_label = ctk.CTkLabel(task_frame, text=info_text, justify="left")
                info_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

                #Task control buttons
                control_frame = ctk.CTkFrame(task_frame)
                control_frame.grid(row=0, column=2, padx=5, pady=5)

                if task.status == TaskStatus.RUNNING:
                    pause_btn = ctk.CTkButton(control_frame, text="⏸️", width=30,
                                            command=lambda tid=task_id: self._pause_task(tid))
                    pause_btn.pack(side="left", padx=2)
                elif task.status == TaskStatus.PAUSED:
                    resume_btn = ctk.CTkButton(control_frame, text="▶️", width=30,
                                             command=lambda tid=task_id: self._resume_task(tid))
                    resume_btn.pack(side="left", padx=2)

                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.PAUSED]:
                    cancel_btn = ctk.CTkButton(control_frame, text="❌", width=30,
                                             command=lambda tid=task_id: self._cancel_task(tid))
                    cancel_btn.pack(side="left", padx=2)

                #Memory info button
                memory_btn = ctk.CTkButton(control_frame, text="💾", width=30,
                                         command=lambda tid=task_id: self._show_task_memory(tid))
                memory_btn.pack(side="left", padx=2)

                self.task_widgets[task_id] = task_frame

            #Schedule next update
            self.after(2000, self._update_task_display)  #Update every 2 seconds

        except Exception as e:
            self.logger.error(f"Error updating task display: {e}")

    def _pause_task(self, task_id: str):
        """Pause a running task."""
        try:
            success = self.task_manager.pause_task(task_id)
            if success:
                self.logger.info(f"Paused task {task_id}")
            else:
                self.logger.warning(f"Failed to pause task {task_id}")
        except Exception as e:
            self.logger.error(f"Error pausing task {task_id}: {e}")

    def _resume_task(self, task_id: str):
        """Resume a paused task."""
        try:
            success = self.task_manager.resume_task(task_id)
            if success:
                self.logger.info(f"Resumed task {task_id}")
            else:
                self.logger.warning(f"Failed to resume task {task_id}")
        except Exception as e:
            self.logger.error(f"Error resuming task {task_id}: {e}")

    def _cancel_task(self, task_id: str):
        """Cancel a task."""
        try:
            success = self.task_manager.cancel_task(task_id)
            if success:
                self.logger.info(f"Cancelled task {task_id}")
            else:
                self.logger.warning(f"Failed to cancel task {task_id}")
        except Exception as e:
            self.logger.error(f"Error cancelling task {task_id}: {e}")

    def _show_task_memory(self, task_id: str):
        """Show memory contents for a specific task."""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                self.logger.warning(f"Task {task_id} not found")
                return

            memories = self.task_manager.memory_manager.search_memories(
                query="",
                collection_names=[task.memory_scope] if hasattr(task, 'memory_scope') else None,
                n_results=100
            )
            memory_count = len(memories) if memories else 0

            #Show simple dialog with memory info
            import tkinter.messagebox as msgbox
            msgbox.showinfo(
                f"Task {task_id} Memory",
                f"Memory Scope: {task.memory_scope}\n"
                f"Memory Entries: {memory_count}\n"
                f"Goal: {task.goal}\n"
                f"Status: {task.status.value}",
            )

        except Exception as e:
            self.logger.error(f"Error showing task memory for {task_id}: {e}")

    def _create_memory_tab(self, tab):
        """Create the widgets for the Memory Viewer tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)  #Let the results frame expand

        #--- Search Frame ---
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=10, padx=10, fill="x")

        self.memory_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search memories...")
        self.memory_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.memory_search_button = ctk.CTkButton(search_frame, text="Search", command=self._search_memory)
        self.memory_search_button.pack(side="left", pady=5, padx=(5, 0))

        #--- Filters and sorting ---
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(filter_frame, text="Collection:").pack(side="left", padx=(10, 5))
        self.collection_var = ctk.StringVar(value="All")

        try:
            if hasattr(self.memory_manager, 'client') and self.memory_manager.client is not None:
                db_collections = self.memory_manager.client.list_collections()
                collection_names = [c.name for c in db_collections]
                collections = ["All"] + collection_names
            else:
                collections = ["All"]
        except Exception as e:
            self.logger.error(f"Could not load memory collections: {e}")
            collections = ["All"]

        self.collection_menu = ctk.CTkOptionMenu(filter_frame, variable=self.collection_var, values=collections)
        self.collection_menu.pack(side="left", padx=5)

        self.refresh_collections_button = ctk.CTkButton(filter_frame, text="Refresh", command=self._refresh_memory_collections, width=80)
        self.refresh_collections_button.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(filter_frame, text="Sort by:").pack(side="left", padx=(20, 5))
        self.sort_var = ctk.StringVar(value="Relevance")
        ctk.CTkRadioButton(filter_frame, text="Relevance", variable=self.sort_var, value="Relevance").pack(side="left", padx=5)
        ctk.CTkRadioButton(filter_frame, text="Date", variable=self.sort_var, value="Date").pack(side="left", padx=5)

        #--- Results Frame ---
        self.memory_results_frame = ctk.CTkScrollableFrame(tab, label_text="Search Results")
        self.memory_results_frame.pack(pady=5, padx=10, fill="both", expand=True)

    def _refresh_memory_collections(self):
        """Reloads the list of memory collections from the database."""
        try:
            if hasattr(self.memory_manager, 'client') and self.memory_manager.client is not None:
                db_collections = self.memory_manager.client.list_collections()
                collection_names = [c.name for c in db_collections]
                collections = ["All"] + collection_names
                self.collection_menu.configure(values=collections)
                self.logger.info("Refreshed memory collection list.")
            else:
                self.logger.warning("Memory manager client not available")
        except Exception as e:
            self.logger.error(f"Failed to refresh memory collections: {e}", exc_info=True)

    def _display_memory_content(self, parent_frame, content_str: str):
        """Tries to parse content as JSON and displays it in a structured way."""
        try:
            data = json.loads(content_str)
            formatted_content = json.dumps(data, indent=2)
            is_json = True
        except (json.JSONDecodeError, TypeError):
            formatted_content = content_str
            is_json = False

        font = ctk.CTkFont(family="monospace", size=12) if is_json else ctk.CTkFont()

        content_label = ctk.CTkLabel(parent_frame, text=formatted_content, font=font, justify="left", wraplength=450)
        content_label.pack(anchor="w", padx=5, pady=5)

    def _search_memory(self):
        query = self.memory_search_entry.get()
        collection = self.collection_var.get()
        sort_by = self.sort_var.get()

        if not query:
            return

        self.logger.info(f"Searching memory for: '{query}' in collection '{collection}'")

        collection_names = None if collection == "All" else [collection]
        results = self.memory_manager.search_memories(query=query, collection_names=collection_names, n_results=20)

        #Sort results if needed
        if sort_by == "Date":
            #Assuming 'timestamp' is stored in metadata, otherwise this will need adjustment
            results.sort(key=lambda r: r.get("metadata", {}).get("timestamp", 0), reverse=True)

        #Clear previous results
        for widget in self.memory_results_frame.winfo_children():
            widget.destroy()

        if not results:
            label = ctk.CTkLabel(self.memory_results_frame, text="No results found.", text_color="gray")
            label.pack(pady=10)
            return

        for res in results:
            content = res.get("content", "N/A")
            metadata = res.get("metadata", {})
            score = res.get("distance", 999)

            frame = ctk.CTkFrame(self.memory_results_frame, border_width=1)
            frame.pack(pady=5, padx=5, fill="x")

            collection_name = res.get("collection", metadata.get("collection", "N/A"))

            header = f"Relevance: {1 - score:.2f} | Collection: {collection_name}"
            header_label = ctk.CTkLabel(frame, text=header, font=ctk.CTkFont(weight="bold"))
            header_label.pack(anchor="w", padx=5, pady=(5,0))

            self._display_memory_content(frame, content)

    def _create_agents_tab(self, tab):
        """Create the widgets for the Agents tab."""
        self._create_agent_list(tab)

    def _create_logs_tab(self, tab):
        """Create the widgets for the Logs & History tab."""
        tab.grid_rowconfigure(0, weight=3)
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        #Reparent and place the pre-existing ChatHistoryView
        self.chat_history_view.master = tab
        self.chat_history_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        self.log_textbox = None
        self.current_plan = None
        self.last_goal = None
        self.log_textbox = ctk.CTkTextbox(tab, font=("monospace", 12), state="disabled")
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

        self._setup_gui_logging()
        self.chat_history_view.add_message("system", "Atlas session started. All actions will be logged here.")
        self.chat_history_view.add_message("agent", "Hello! I'm Atlas. Please provide your goal in the 'Master Agent' tab.")

    def _create_settings_tab(self, tab):
        """Create the widgets for the Settings tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(4, weight=1) #Allow rules textbox to expand

        #--- API Keys Frame ---
        api_keys_frame = ctk.CTkFrame(tab)
        api_keys_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        api_keys_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(api_keys_frame, text="API Keys", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        ctk.CTkLabel(api_keys_frame, text="OpenAI API Key").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.openai_api_key_entry = ctk.CTkEntry(api_keys_frame, textvariable=self.openai_api_key_var, show="*")
        self.openai_api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(api_keys_frame, text="Gemini API Key").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.gemini_api_key_entry = ctk.CTkEntry(api_keys_frame, textvariable=self.gemini_api_key_var, show="*")
        self.gemini_api_key_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(api_keys_frame, text="Groq API Key").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.groq_api_key_entry = ctk.CTkEntry(api_keys_frame, textvariable=self.groq_api_key_var, show="*")
        self.groq_api_key_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(api_keys_frame, text="Mistral API Key").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.mistral_api_key_entry = ctk.CTkEntry(api_keys_frame, textvariable=self.mistral_api_key_var, show="*")
        self.mistral_api_key_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(api_keys_frame, text="Anthropic API Key").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.anthropic_api_key_entry = ctk.CTkEntry(api_keys_frame, textvariable=self.anthropic_api_key_var, show="*")
        self.anthropic_api_key_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        #--- Plugin Management Frame ---
        plugin_outer_frame = ctk.CTkFrame(tab)
        plugin_outer_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        plugin_outer_frame.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1) #Allow plugin frame to expand

        plugin_header_frame = ctk.CTkFrame(plugin_outer_frame, fg_color="transparent")
        plugin_header_frame.pack(fill="x", padx=10, pady=(5, 10))
        plugin_header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(plugin_header_frame, text="Plugin Management", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")

        plugin_buttons_frame = ctk.CTkFrame(plugin_header_frame, fg_color="transparent")
        plugin_buttons_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(plugin_buttons_frame, text="Enable All", width=90, command=self._toggle_all_plugins_enabled).pack(side="left", padx=5)
        ctk.CTkButton(plugin_buttons_frame, text="Disable All", width=90, command=lambda: self._toggle_all_plugins_enabled(False)).pack(side="left")

        self.plugin_scroll_frame = ctk.CTkScrollableFrame(plugin_outer_frame, label_text="Available Plugins")
        self.plugin_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._populate_plugin_frame()

        #--- Token Usage Statistics ---
        token_frame = ctk.CTkFrame(tab)
        token_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        token_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(token_frame, text="Token Usage Statistics", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=(5,10), sticky="w")

        ctk.CTkLabel(token_frame, text="Prompt:").grid(row=1, column=0, padx=10, pady=2, sticky="w")
        self.prompt_tokens_label = ctk.CTkLabel(token_frame, text="0")
        self.prompt_tokens_label.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(token_frame, text="Completion:").grid(row=2, column=0, padx=10, pady=2, sticky="w")
        self.completion_tokens_label = ctk.CTkLabel(token_frame, text="0")
        self.completion_tokens_label.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(token_frame, text="Total:").grid(row=3, column=0, padx=10, pady=2, sticky="w")
        self.total_tokens_label = ctk.CTkLabel(token_frame, text="0", font=ctk.CTkFont(weight="bold"))
        self.total_tokens_label.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        self.reset_tokens_button = ctk.CTkButton(token_frame, text="Reset", command=self._reset_token_stats)
        self.reset_tokens_button.grid(row=1, column=2, rowspan=3, padx=10, pady=5)

        #--- Save Button ---
        self.save_settings_button = ctk.CTkButton(tab, text="Save Settings", command=self._save_settings)
        self.save_settings_button.grid(row=6, column=0, padx=10, pady=10, sticky="s")

    def _populate_plugin_frame(self):
        """Populates the plugin scrollable frame with checkboxes for each plugin."""
        #Clear existing widgets from the scrollable frame
        for widget in self.plugin_scroll_frame.winfo_children():
            widget.destroy()

        all_plugins = self.plugin_manager.get_all_plugins()
        if not all_plugins:
            ctk.CTkLabel(self.plugin_scroll_frame, text="No plugins found.", text_color="gray").pack(padx=10, pady=10)
        else:
            for plugin_id, plugin_data in sorted(all_plugins.items()):
                manifest = plugin_data.get("manifest", {})
                plugin_name = manifest.get("name", plugin_id)

                if plugin_id not in self.plugin_enabled_vars:
                    #Initialize based on loaded settings or default to True
                    is_enabled = self.loaded_settings.get("plugins", {}).get(plugin_id, True)
                    self.plugin_enabled_vars[plugin_id] = ctk.BooleanVar(value=is_enabled)

                var = self.plugin_enabled_vars[plugin_id]
                cb = ctk.CTkCheckBox(self.plugin_scroll_frame, text=plugin_name, variable=var)
                cb.pack(fill="x", padx=10, pady=5)

    def _toggle_all_plugins_enabled(self, enable: bool = True):
        """Enables or disables all plugin checkboxes."""
        for var in self.plugin_enabled_vars.values():
            var.set(enable)

    def _on_run(self):
        goal_input = self.goal_text.get("1.0", "end").strip()
        if not goal_input:
            self.chat_history_view.add_message("system", "Please enter a goal before running.")
            return

        self.last_goal = goal_input
        self.feedback_frame.grid_remove()
        self.good_button.configure(state="disabled")
        self.bad_button.configure(state="disabled")
        prompt = self.prompt_text.get("1.0", "end").strip()
        options = {
            "goal_list": self.goal_list_var.get(),
            "cyclic": self.cyclic_var.get(),
        }

        #Update status panel
        if hasattr(self, "status_panel"):
            self.status_panel.update_status("Starting", "Checking security", 10)
            self.status_panel.add_log_entry(f"Starting goal execution: {goal_input[:50]}...", "INFO", "MasterAgent")

        security_event = {
            "type": "GOAL_EXECUTION_REQUEST",
            "source": "AtlasApp",
            "details": {"goal": goal_input, "prompt": prompt, "options": options},
        }
        self.security_agent_conn.send(security_event)
        self.logger.info("Waiting for security approval...")

        response = self.security_agent_conn.recv()

        if response.get("action") == "ALLOW":
            self.logger.info("Security Agent approved execution.")

            #Update status panel
            if hasattr(self, "status_panel"):
                self.status_panel.update_status("Running", "Executing goal", 20)
                self.status_panel.add_log_entry("Security approval granted", "SUCCESS", "SecurityAgent")

            self.run_button.configure(text="Running...", state="disabled")
            self.progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
            self.progress_bar.start()

            #Add goal to history as "In Progress"
            self.goal_history_manager.add_goal(goal_input, "In Progress")

            if options["goal_list"]:
                goals = [g.strip() for g in goal_input.split("\n") if g.strip()]
                # Convert goals list to a single string since run expects a string
                goal_string = "\n".join(goals)
                context = {"prompt": prompt, "options": options}
                self.master_agent.run(goal_string, context)
            else:
                context = {"prompt": prompt, "options": options}
                self.master_agent.run(goal_input, context)

            self._check_agent_status()
        else:
            reason = response.get("reason", "No reason provided.")
            self.logger.warning(f"Execution blocked by Security Agent. Reason: {reason}")
            self.chat_history_view.add_message("system", f"Execution blocked by Security Agent: {reason}")

            #Update status panel
            if hasattr(self, "status_panel"):
                self.status_panel.update_status("Blocked", "Security denied execution", 0)
                self.status_panel.add_log_entry(f"Execution blocked: {reason}", "ERROR", "SecurityAgent")

            #Add to goal history as "Cancelled"
            self.goal_history_manager.add_goal(goal_input, "Cancelled", error_message=reason)

    def _on_pause(self):
        self.logger.info("Pause clicked")
        self.master_agent.pause()

    def _on_stop(self):
        self.logger.info("Stop clicked")
        self.master_agent.stop()

        #Update status panel
        if hasattr(self, "status_panel"):
            self.status_panel.update_status("Stopped", "Execution cancelled by user", 0)
            self.status_panel.add_log_entry("Execution stopped by user", "WARNING", "System")

        #Update goal history if there was a running goal
        if self.last_goal:
            self.goal_history_manager.add_goal(self.last_goal, "Cancelled", error_message="Stopped by user")

    def _check_agent_status(self):
        """Periodically check if the agent thread is alive and update UI."""
        if self.master_agent.is_running:
            self.after(100, self._check_agent_status)
        else:
            self._on_agent_complete()

    def _on_agent_complete(self):
        """Reset the UI after the agent has finished its task."""
        self.logger.info("Agent task finished. Resetting UI.")
        self.run_button.configure(text="Run", state="normal")
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.feedback_frame.grid()
        self.good_button.configure(state="normal")
        self.bad_button.configure(state="normal")

        #Update status panel
        if hasattr(self, "status_panel"):
            self.status_panel.update_status("Idle", "Waiting for next goal", 0)

    def _handle_feedback(self, positive: bool):
        """Handles user feedback submission."""
        self.logger.info(f"User feedback received: {'Positive' if positive else 'Negative'}")
        if self.last_goal:
            self.master_agent.record_feedback(f"Goal: {self.last_goal}, Feedback: {'Positive' if positive else 'Negative'}")
            self.chat_history_view.add_message("system", "Feedback recorded. Thank you!")
            self.good_button.configure(state="disabled")
            self.bad_button.configure(state="disabled")



    def _update_plugins_from_settings(self, plugins_enabled: Dict[str, bool]):
        """Updates the agent manager based on the provided plugin states."""
        #Only clear tools if this is not the initial load
        if hasattr(self, "_initial_settings_applied"):
            self.agent_manager.clear_tools()

        all_plugins = self.plugin_manager.get_all_plugins()

        for plugin_id, plugin_data in all_plugins.items():
            #If no setting exists, default to enabled
            if plugins_enabled.get(plugin_id, True):
                for tool_instance in plugin_data.get("tools", []):
                    for tool_name in dir(tool_instance):
                        if not tool_name.startswith("_"):
                            tool_function = getattr(tool_instance, tool_name)
                            if callable(tool_function):
                                self.agent_manager.add_tool(
                                    name=tool_name,
                                    tool_function=tool_function,
                                    description=getattr(tool_function, "__doc__", "No description available."),
                                )
                for agent_class in plugin_data.get("agents", []):
                    # Create an instance of the agent class if it's a class, not an instance
                    if isinstance(agent_class, type):
                        agent_instance = agent_class(llm_manager=self.llm_manager)
                    else:
                        agent_instance = agent_class
                    self.agent_manager.add_agent(agent_class.__name__ if hasattr(agent_class, '__name__') else str(agent_class), agent_instance)
        self.logger.info(f"Updated agent tools based on settings. Active tools: {self.agent_manager.get_tool_names()}")

        #Mark that initial settings have been applied
        self._initial_settings_applied = True

    def _on_plugin_toggle(self, plugin_id: str, enabled: bool):
        """Callback when a plugin checkbox is toggled. No immediate save."""
        self.logger.info(f"Plugin '{plugin_id}' toggled to {'enabled' if enabled else 'disabled'} in UI. Save settings to apply.")

    def _update_token_stats(self):
        """Periodically updates the token usage statistics in the UI."""
        if self.token_tracker:
            stats = self.token_tracker.get_usage()
            if self.prompt_tokens_label:
                self.prompt_tokens_label.configure(text=str(stats.prompt_tokens))
            if self.completion_tokens_label:
                self.completion_tokens_label.configure(text=str(stats.completion_tokens))
            if self.total_tokens_label:
                self.total_tokens_label.configure(text=str(stats.total_tokens))

        self.after(1000, self._update_token_stats)

    def _reset_token_stats(self):
        """Resets the token tracker and updates the UI."""
        if self.token_tracker:
            self.token_tracker.reset()
            self.logger.info("Token usage statistics have been reset.")

    def _save_settings(self):
        """Save all current settings to the config file and update agents."""
        self.logger.info("Saving all settings...")
        try:
            #Plugin settings
            enabled_plugins = {name: var.get() for name, var in self.plugin_enabled_vars.items()}

            #Security settings
            rules = self.security_rules_text.get("1.0", "end-1c").split("\n")
            security_config = {
                "destructive_op_threshold": self.destructive_slider.get(),
                "api_usage_threshold": self.api_usage_slider.get(),
                "file_access_threshold": self.file_access_slider.get(),
                "rules": [r for r in rules if r.strip()],
                "notifications": {
                    "email": self.notification_email_var.get(),
                    "telegram": self.notification_telegram_var.get(),
                    "sms": self.notification_sms_var.get(),
                },
            }

            #Agent settings
            agent_config = {}
            for agent_card in self.agent_cards:
                agent_config[agent_card["name"]] = {
                    "provider": agent_card["provider_menu"].get(),
                    "model": agent_card["model_menu"].get(),
                    "fallback_chain": agent_card["fallback_chain"],
                }

            #API keys
            api_keys_config = {
                "openai": self.openai_api_key_var.get(),
                "gemini": self.gemini_api_key_var.get(),
                "anthropic": self.anthropic_api_key_var.get(),
                "groq": self.groq_api_key_var.get(),
                "mistral": self.mistral_api_key_var.get(),
            }

            #Combine all settings
            all_settings = {
                "api_keys": api_keys_config,
                "plugins_enabled": enabled_plugins,
                "security": security_config,
                "agents": agent_config,
            }

            self.config_manager.save(all_settings)
            self.loaded_settings = all_settings

            #Apply relevant settings immediately
            self._update_plugins_from_settings(enabled_plugins)
            self.master_agent.llm_manager.update_settings()

            #Update chat translation manager with current LLM manager
            if hasattr(self, "chat_translation_manager"):
                self.chat_translation_manager.set_llm_manager(self.master_agent.llm_manager)

            #Send updated settings to the security agent process
            notifications = security_config.get("notifications", {})
            self.security_agent_conn.send({
                "type": "UPDATE_RULES",
                "details": {"rules": security_config.get("rules", [])},
            })
            self.security_agent_conn.send({
                "type": "UPDATE_NOTIFICATION_SETTINGS",
                "details": {"channels": notifications},
            })

            self.chat_history_view.add_message("system", "All settings saved and applied successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}", exc_info=True)
            self.chat_history_view.add_message("system", "Error: Failed to save settings. Check logs.")

    def _load_settings(self):
        """Load settings from the config file into memory."""
        self.logger.info("Loading all settings...")
        self.loaded_settings = self.config_manager.load()
        if not self.loaded_settings:
            self.logger.warning("Could not load settings, using defaults.")
            self.loaded_settings = {} #Ensure it's a dict

    def _apply_settings_to_ui(self):
        """Apply loaded settings to the GUI widgets."""
        self.logger.info("Applying settings to UI...")
        settings = self.loaded_settings
        if not settings:
            self.logger.warning("No settings loaded, UI will use defaults.")
            self._populate_plugin_frame() #Populate with default values
            return

        #Apply API key settings
        self.openai_api_key_var.set(settings.get("api_keys", {}).get("openai", ""))
        self.gemini_api_key_var.set(settings.get("api_keys", {}).get("gemini", ""))
        self.anthropic_api_key_var.set(settings.get("api_keys", {}).get("anthropic", ""))
        self.groq_api_key_var.set(settings.get("api_keys", {}).get("groq", ""))
        self.mistral_api_key_var.set(settings.get("api_keys", {}).get("mistral", ""))

        #Apply plugin settings
        enabled_plugins = settings.get("plugins_enabled", {})
        self._update_plugins_from_settings(enabled_plugins)

        #Apply security settings
        security_config = settings.get("security", {})
        self.destructive_slider.set(security_config.get("destructive_op_threshold", 80))
        self.api_usage_slider.set(security_config.get("api_usage_threshold", 80))
        self.file_access_slider.set(security_config.get("file_access_threshold", 80))
        self.security_rules_text.delete("1.0", "end")
        self.security_rules_text.insert("1.0", "\n".join(security_config.get("rules", [])))
        notifications = security_config.get("notifications", {})
        self.notification_email_var.set(notifications.get("email", False))
        self.notification_telegram_var.set(notifications.get("telegram", False))
        self.notification_sms_var.set(notifications.get("sms", False))

        #Send updated settings to the security agent process
        self.security_agent_conn.send({
            "type": "UPDATE_RULES",
            "details": {"rules": security_config.get("rules", [])},
        })
        self.security_agent_conn.send({
            "type": "UPDATE_NOTIFICATION_SETTINGS",
            "details": {"channels": notifications},
        })

        #Apply agent settings
        agent_config = settings.get("agents", {})
        for agent_card in self.agent_cards:
            card_config = agent_config.get(agent_card["name"], {})
            agent_card["provider_menu"].set(card_config.get("provider", "ollama"))
            self._update_model_menu(agent_card["provider_menu"].get(), agent_card["model_menu"])
            agent_card["model_menu"].set(card_config.get("model", ""))
            agent_card["fallback_chain"] = card_config.get("fallback_chain", [])
        self.master_agent.llm_manager.update_settings()

        #Update chat translation manager with current LLM manager
        if hasattr(self, "chat_translation_manager"):
            self.chat_translation_manager.set_llm_manager(self.master_agent.llm_manager)

        self.logger.info("All settings loaded and applied.")
        self.chat_history_view.add_message("system", "Settings loaded successfully.")



    def _load_app_state(self):
        """Loads the application state from a file."""
        try:
            with open("state.json") as f:
                state = json.load(f)
        except FileNotFoundError:
            self.logger.info("No previous state file found. Starting fresh.")
            return
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Failed to load application state: {e}")
            return

        if state:
            self.goal_text.insert("1.0", state.get("goal_input", ""))
            self.prompt_text.insert("1.0", state.get("prompt_input", ""))
            self.chat_history_view.load_history(state.get("chat_history", []))
            self.logger.info("Application state loaded.")

    def _log_loaded_plugins(self):
        """Logs the names of all discovered plugins."""
        all_plugins = self.plugin_manager.get_all_plugins()
        if all_plugins:
            plugin_names = [p.get("manifest", {}).get("name", pid) for pid, p in all_plugins.items()]
            self.logger.info(f"Discovered plugins: {', '.join(plugin_names)}")
        else:
            self.logger.info("No plugins found in the 'plugins' directory.")

    def _on_close(self):
        """Handle window closing event by saving state and stopping agents."""
        self.logger.info("AtlasApp closing...")
        self._save_app_state()
        self._save_settings()

        self.master_agent.stop()
        self.deputy_agent.stop()
        self.security_agent.stop()

        if self.master_agent.thread and self.master_agent.thread.is_alive():
            self.master_agent.thread.join(timeout=2)
        if self.deputy_agent.thread and self.deputy_agent.thread.is_alive():
            self.deputy_agent.thread.join(timeout=2)
        if self.security_agent.monitoring_thread and self.security_agent.monitoring_thread.is_alive():
            self.security_agent.monitoring_thread.join(timeout=2)

        self.destroy()

    def _setup_gui_logging(self):
        """Configure the logger to output to the GUI textbox."""
        gui_handler = GuiLogger(self.log_textbox)
        gui_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%H:%M:%S"),
        )
        add_handler(gui_handler)
        self.logger.info("GUI logging configured.")

    def _create_agent_list(self, tab):
        """Create and populate the list of specialized agents."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1) #Allow scrollable frame to expand

        scrollable_frame = ctk.CTkScrollableFrame(tab, label_text="Available Agents")
        scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)

        agents = self.agent_manager._agents
        if not agents:
            ctk.CTkLabel(scrollable_frame, text="No specialized agents available.").pack(pady=10)
            return

        for i, (agent_name, agent_instance) in enumerate(agents.items()):
            agent_card = ctk.CTkFrame(scrollable_frame, border_width=1)
            agent_card.grid(row=i, column=0, padx=10, pady=(5, 10), sticky="ew")
            agent_card.grid_columnconfigure(0, weight=1)

            #Agent Name (Title)
            ctk.CTkLabel(agent_card, text=agent_name, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

            #Agent Description from docstring
            description = inspect.getdoc(agent_instance) or "No description available."
            ctk.CTkLabel(agent_card, text=description, wraplength=800, justify="left").grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        #Add buttons below the scrollable frame
        button_frame = ctk.CTkFrame(tab)
        button_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")
        ctk.CTkButton(button_frame, text="Save All Agents", command=self._save_settings).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Load All Agents", command=self._load_settings).pack(side="left", padx=5)


    def _create_performance_tab(self, tab):
        """Creates the UI for the Performance Monitoring tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        label = ctk.CTkLabel(tab, text="Performance metrics will be displayed here.", font=ctk.CTkFont(size=14))
        #--- Performance Charts ---
        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(1, 2, 1)
        self.ax2 = self.fig.add_subplot(1, 2, 2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        #--- Controls ---
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(pady=5, padx=10, fill="x")
        self.refresh_perf_button = ctk.CTkButton(controls_frame, text="Refresh Data", command=self._update_performance_charts)
        self.refresh_perf_button.pack(side="left", padx=5)

        self.clear_perf_button = ctk.CTkButton(controls_frame, text="Clear Data", command=self._clear_performance_data, fg_color="#c0392b", hover_color="#e74c3c")
        self.clear_perf_button.pack(side="left", padx=5)

        self._update_performance_charts() #Initial data load


    def _update_performance_charts(self):
        """Fetches performance data from MetricsManager and redraws the charts."""
        self.logger.info("Updating performance charts with live data...")

        tool_load_times = metrics_manager.get_tool_load_times()
        memory_search_latencies = metrics_manager.get_memory_search_latencies()

        #--- Chart 1: Tool Loading Time ---
        self.ax1.clear()
        if tool_load_times:
            self.ax1.bar(tool_load_times.keys(), tool_load_times.values(), color="skyblue")
        self.ax1.set_title("Tool Loading Time (s)")
        self.ax1.set_ylabel("Seconds")
        self.ax1.tick_params(axis="x", rotation=45)

        #--- Chart 2: Memory Search Latency ---
        self.ax2.clear()
        if memory_search_latencies:
            self.ax2.plot(memory_search_latencies, marker="o", linestyle="-", color="lightcoral")
        self.ax2.set_title("Memory Search Latency (s)")
        self.ax2.set_xlabel("Search Event")
        self.ax2.set_ylabel("Seconds")

        self.fig.tight_layout()
        self.canvas.draw()

    def _clear_performance_data(self):
        """Clears all performance data and refreshes the charts."""
        self.logger.info("Clearing all performance data.")
        metrics_manager.clear_data()
        self._update_performance_charts()

    def _create_security_tab(self, tab):
        """Create and populate the security settings tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        #--- Settings Frame ---
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)

        #--- Sliders ---
        ctk.CTkLabel(settings_frame, text="Destructive Op Confirmation Threshold").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.destructive_slider = ctk.CTkSlider(settings_frame, from_=0, to=100, number_of_steps=10)
        self.destructive_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.destructive_slider.set(80)

        ctk.CTkLabel(settings_frame, text="API Usage Alert Threshold").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.api_usage_slider = ctk.CTkSlider(settings_frame, from_=0, to=100, number_of_steps=10)
        self.api_usage_slider.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.api_usage_slider.set(50)

        ctk.CTkLabel(settings_frame, text="File Access Warning Threshold").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.file_access_slider = ctk.CTkSlider(settings_frame, from_=0, to=100, number_of_steps=10)
        self.file_access_slider.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.file_access_slider.set(70)

        #--- Rules Textbox ---
        ctk.CTkLabel(tab, text="Security Rules (one per line)").grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.security_rules_text = ctk.CTkTextbox(tab, height=150)
        self.security_rules_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.security_rules_text.insert("1.0", "#Example Rule: Deny all shell commands that contain 'rm -rf'\nDENY,TERMINAL,.*rm -rf.*")

        #--- Plugin Management Frame ---
        plugin_frame = ctk.CTkFrame(tab)
        plugin_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        plugin_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(plugin_frame, text="Plugin Management", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w",
        )

        all_plugins = self.plugin_manager.get_all_plugins()
        row = 1
        if not all_plugins:
            ctk.CTkLabel(plugin_frame, text="No plugins found.", text_color="gray").grid(
                row=row, column=0, columnspan=2, padx=10, pady=5, sticky="w",
            )
        else:
            for plugin_id, plugin_data in all_plugins.items():
                manifest = plugin_data.get("manifest", {})
                plugin_name = manifest.get("name", plugin_id)
                description = manifest.get("description", "No description provided.")

                var = ctk.BooleanVar()
                self.plugin_enabled_vars[plugin_id] = var

                cb = ctk.CTkCheckBox(plugin_frame, text=plugin_name, variable=var)
                cb.grid(row=row, column=0, padx=10, pady=5, sticky="w")
                #Add a tooltip for the description
                #Note: CTk doesn't have a built-in tooltip, this is a conceptual placeholder.
                #A more advanced implementation would use a custom tooltip class.
                desc_label = ctk.CTkLabel(plugin_frame, text=f"({description})", text_color="gray")
                desc_label.grid(row=row, column=1, padx=10, pady=5, sticky="w")
                row += 1

        #--- Bottom Frame for Notifications and Buttons ---
        bottom_frame = ctk.CTkFrame(tab)
        bottom_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)

        #Notification Channels
        notification_frame = ctk.CTkFrame(bottom_frame)
        notification_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(notification_frame, text="Notification Channels:").pack(side="left", padx=(10, 5))
        ctk.CTkCheckBox(notification_frame, text="Email", variable=self.notification_email_var).pack(side="left", padx=5)
        ctk.CTkCheckBox(notification_frame, text="Telegram", variable=self.notification_telegram_var).pack(side="left", padx=5)
        ctk.CTkCheckBox(notification_frame, text="SMS", variable=self.notification_sms_var).pack(side="left", padx=5)

        #Save/Load Buttons
        button_frame = ctk.CTkFrame(bottom_frame)
        button_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(button_frame, text="Save Settings", command=self._save_settings).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Load Settings", command=self._load_settings).pack(side="left", padx=5)

    def _create_status_tab(self, tab):
        """Create the enhanced status monitoring tab."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        #Create status panel
        self.status_panel = StatusPanel(tab)
        self.status_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        #Add some initial log entries
        self.status_panel.add_log_entry("Atlas system initialized", "INFO", "System")
        self.status_panel.add_log_entry("All agents started successfully", "SUCCESS", "System")

    def _create_enhanced_settings_tab(self, tab):
        """Create the enhanced settings tab with comprehensive options."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        #Create enhanced settings view
        self.enhanced_settings = EnhancedSettingsView(
            tab,
            config_manager=self.config_manager,
            plugin_manager=self.plugin_manager,
            save_callback=self._on_enhanced_settings_save,
        )
        self.enhanced_settings.grid(row=0, column=0, sticky="nsew")

    def _on_enhanced_settings_save(self, settings: Dict[str, Any]):
        """Handle saving of enhanced settings."""
        try:
            #Apply theme change if needed
            if "theme" in settings:
                ctk.set_appearance_mode(settings["theme"])

            #Update LLM manager settings
            if hasattr(self, "llm_manager"):
                #Update provider and model if specified
                current_provider = settings.get("current_provider")
                current_model = settings.get("current_model")

                if current_provider and current_model:
                    # TODO: Implement set_provider_and_model method in LLMManager
                    # self.llm_manager.set_provider_and_model(current_provider, current_model)
                    self.logger.info(f"LLM provider setting request: {current_provider} with model {current_model}")

                #Refresh all LLM clients with new API keys
                # TODO: Implement update_settings method in LLMManager
                # self.llm_manager.update_settings()

                #Update master agent's LLM manager if needed
                if hasattr(self, "master_agent") and hasattr(self.master_agent, "llm_manager"):
                    self.master_agent.llm_manager = self.llm_manager

                #Update chat translation manager with current LLM manager
                if hasattr(self, "chat_translation_manager"):
                    self.chat_translation_manager.set_llm_manager(self.llm_manager)

            #Update security agent settings if needed
            security_settings = {
                "file_access_threshold": settings.get("file_access_threshold"),
                "system_cmd_threshold": settings.get("system_cmd_threshold"),
                "network_threshold": settings.get("network_threshold"),
                "restricted_directories": settings.get("restricted_directories", []),
            }

            if hasattr(self, "security_agent"):
                security_message = {
                    "type": "update_settings",
                    "data": {"settings": security_settings},
                }
                try:
                    self.security_agent_conn.send(security_message)
                except Exception as e:
                    self.logger.warning(f"Could not update security agent settings: {e}")

            #Update plugin states
            plugin_states = settings.get("plugin_enabled_states", {})
            for plugin_id, enabled in plugin_states.items():
                try:
                    if enabled:
                        self.plugin_manager.enable_plugin(plugin_id)
                    else:
                        self.plugin_manager.disable_plugin(plugin_id)
                except Exception as e:
                    self.logger.warning(f"Could not update plugin {plugin_id}: {e}")

            self.logger.info("Enhanced settings applied successfully")
        except Exception as e:
            self.logger.error(f"Error applying enhanced settings: {e}")

    def _open_goal_history(self):
        """Open the goal history window."""
        GoalHistoryWindow(self, goal_callback=self._run_goal_from_history)

    def _run_goal_from_history(self, goal_text: str):
        """Run a goal selected from history."""
        self.goal_text.delete(1.0, ctk.END)
        self.goal_text.insert(1.0, goal_text)
        self._on_run()

    def _open_enhanced_plugin_manager(self):
        """Open the enhanced plugin manager window."""
        EnhancedPluginManagerWindow(self, self.plugin_manager)

    def _update_preview(self):
        try:
            img = capture_screen()
            img.thumbnail((400, 250))
            tk_img = CTkImage(light_image=img, dark_image=img, size=img.size)
            self.preview_label.configure(image=tk_img, text="")
            self.preview_label.image = tk_img  #keep reference
        except Exception as exc:  #pragma: no cover
            self.preview_label.configure(text=f"Preview error: {exc}")
        #schedule next update
        self.after(2000, self._update_preview)



    def _save_app_state(self):
        """Saves the current state of the application to a file."""
        state = {
            "goal_input": self.goal_text.get("1.0", "end-1c"),
            "prompt_input": self.prompt_text.get("1.0", "end-1c"),
            "chat_history": self.chat_history_view.get_history(),
        }
        try:
            with open("state.json", "w") as f:
                json.dump(state, f, indent=4)
            self.logger.info("Application state saved.")
        except Exception as e:
            self.logger.error(f"Failed to save application state: {e}")

    def _copy_input_text(self):
        """Copies the selected text from the chat input to the clipboard."""
        try:
            selected_text = self.chat_input.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected, do nothing
            pass

    def _create_chat_tab(self, tab):
        """Creates the interactive chat interface for user-Atlas communication."""
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        #Main chat frame
        chat_frame = ctk.CTkFrame(tab)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)

        #Chat history view
        self.chat_view = ChatHistoryView(chat_frame)
        self.chat_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        #Context indicator frame
        context_frame = ctk.CTkFrame(chat_frame)
        context_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        context_frame.grid_columnconfigure(6, weight=1)

        #Mode control section
        ctk.CTkLabel(context_frame, text="Mode:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=(10, 5), pady=5, sticky="w",
        )

        #Auto mode toggle button
        self.auto_mode_button = ctk.CTkButton(
            context_frame,
            text="Auto: ON",
            command=self._toggle_auto_mode,
            width=80,
            height=28,
            fg_color="green",
        )
        self.auto_mode_button.grid(row=0, column=1, padx=5, pady=5)

        #Mode buttons (for manual control)
        self.chat_mode_button = ctk.CTkButton(
            context_frame,
            text="💬 Chat",
            command=lambda: self._set_manual_mode(ChatMode.CASUAL_CHAT),
            width=60,
            height=28,
            state="normal",  #Always enabled
        )
        self.chat_mode_button.grid(row=0, column=2, padx=2, pady=5)

        self.help_mode_button = ctk.CTkButton(
            context_frame,
            text="❓ Help",
            command=lambda: self._set_manual_mode(ChatMode.SYSTEM_HELP),
            width=60,
            height=28,
            state="normal",  #Always enabled
        )
        self.help_mode_button.grid(row=0, column=3, padx=2, pady=5)

        self.goal_mode_button = ctk.CTkButton(
            context_frame,
            text="🎯 Goal",
            command=lambda: self._set_manual_mode(ChatMode.GOAL_SETTING),
            width=60,
            height=28,
            state="normal",  #Always enabled
        )
        self.goal_mode_button.grid(row=0, column=4, padx=2, pady=5)

        #Development mode button (special styling)
        self.dev_mode_button = ctk.CTkButton(
            context_frame,
            text="🔧 Dev",
            command=self._set_development_mode,
            width=60,
            height=28,
            fg_color="orange",
            hover_color="red",
        )
        self.dev_mode_button.grid(row=0, column=5, padx=5, pady=5)

        #Current mode indicator
        self.current_mode_label = ctk.CTkLabel(
            context_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
        )
        self.current_mode_label.grid(row=0, column=6, padx=5, pady=5, sticky="w")

        #Translation status indicator
        self.translation_status_label = ctk.CTkLabel(
            context_frame,
            text="🌐 Translation: Ready",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        self.translation_status_label.grid(row=0, column=7, padx=5, pady=5, sticky="e")

        #Clear context button
        self.clear_context_button = ctk.CTkButton(
            context_frame,
            text="Clear",
            command=self._clear_chat_context,
            width=60,
            height=28,
        )
        self.clear_context_button.grid(row=0, column=8, padx=(5, 10), pady=5, sticky="e")

        #Input frame
        input_frame = ctk.CTkFrame(chat_frame)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        # Add top frame for input copy button
        input_top_frame = ctk.CTkFrame(input_frame, height=30)
        input_top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
        input_top_frame.grid_columnconfigure(1, weight=1)

        # Input copy button (small and subtle)
        self.input_copy_button = ctk.CTkButton(
            input_top_frame,
            text="📋",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="gray50",
            hover_color="gray30",
            command=self._copy_input_text,
        )
        self.input_copy_button.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        #Chat input textbox
        self.chat_input = ctk.CTkTextbox(input_frame, height=80, wrap="word")
        self.chat_input.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=10)

        #Enable formatting context menu for chat input
        enable_formatting_context_menu(self.chat_input, self.chat_context_manager)

        #Send button
        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self._send_chat_message,
            width=80,
        )
        self.send_button.grid(row=1, column=1, sticky="ns", padx=(5, 10), pady=10)

        #Bind Enter key to send message (Ctrl+Enter for new line)
        self.chat_input.bind("<Return>", self._on_enter_key)
        self.chat_input.bind("<Control-Return>", self._on_ctrl_enter)

        #Add initial welcome message with context explanation
        welcome_message = """Hello! I'm Atlas, your AI assistant. 

I can understand different types of conversations:
🎯 **Goals** - Tasks you want me to perform
💬 **Chat** - General conversation and questions  
❓ **Help** - Information about my features
🔧 **Tools** - Questions about available tools
📊 **Status** - System status and performance
⚙️ **Config** - Help with settings and configuration

The current mode will be shown above. How can I help you today?"""

        self.chat_view.add_message("assistant", welcome_message)

    def _send_chat_message(self):
        """Handles sending a chat message to Atlas."""
        message = self.chat_input.get("1.0", "end").strip()
        if not message:
            return

        #Clear the input
        self.chat_input.delete("1.0", "end")

        #Add user message to chat
        self.chat_view.add_message("user", message)

        #Check if any LLM provider is available
        if not hasattr(self.master_agent, "llm_manager") or not self.master_agent.llm_manager:
            self.chat_view.add_message("assistant", "I'm sorry, but I don't have access to an LLM client. Please configure an API key for any supported provider (OpenAI, Gemini, Groq, Mistral, or Ollama) in the LLM Settings tab.")
            return

        #Check current provider availability
        llm_manager = self.master_agent.llm_manager
        current_provider = llm_manager.current_provider
        provider_available = llm_manager.is_provider_available(current_provider)

        if not provider_available:
            available_providers = [p for p in ["openai", "gemini", "groq", "mistral", "ollama"]
                                 if llm_manager.is_provider_available(p)]
            if available_providers:
                self.chat_view.add_message("assistant", f"Current provider '{current_provider}' is not available. Available providers: {', '.join(available_providers)}. Please change your provider in LLM Settings.")
            else:
                self.chat_view.add_message("assistant", "No LLM providers are currently available. Please configure API keys in the LLM Settings tab.")
            return

        #Process the message through Atlas
        try:
            #Use the master agent to process the message
            self.chat_view.add_message("assistant", "Processing your request...")

            #Run in a separate thread to avoid blocking the UI
            import threading
            threading.Thread(
                target=self._process_chat_message,
                args=(message,),
                daemon=True,
            ).start()

        except Exception as e:
            self.chat_view.add_message("assistant", f"Sorry, I encountered an error: {e!s}")

    def _process_chat_message(self, message: str):
        """Process the chat message using enhanced context analysis and translation."""
        try:
            #Check if we have a working LLM manager
            if not hasattr(self.master_agent, "llm_manager") or not self.master_agent.llm_manager:
                self.after(0, lambda: self.chat_view.add_message("assistant", "LLM manager not available."))
                return

            #Update translation manager with current LLM manager
            self.chat_translation_manager.set_llm_manager(self.master_agent.llm_manager)

            #Process incoming message through translation if needed
            processed_message, translation_context = self.chat_translation_manager.process_incoming_message(message)

            #Check for creator authentication before processing
            creator_identity_level = self.creator_auth.process_message_for_creator_detection(processed_message)

            #If detected as possible creator, initiate authentication
            if creator_identity_level == CreatorIdentityLevel.POSSIBLE_CREATOR:
                auth_result = self.creator_auth.initiate_creator_authentication(creator_identity_level)
                if auth_result.get("requires_authentication", False):
                    auth_message = auth_result["message"]
                    # Force immediate UI update
                    self.chat_view.add_message("assistant", auth_message)
                    # Also update display to ensure visibility
                    self.update_idletasks()

                #Store the challenge state for next message
                self._waiting_for_creator_response = True
                self._original_message_for_processing = processed_message
                self._translation_context = translation_context
                return

            if hasattr(self, "_waiting_for_creator_response") and self._waiting_for_creator_response:
                #Process challenge response
                success, auth_response = self.creator_auth.validate_challenge_response(processed_message)
                # Force immediate UI update for challenge response
                self.chat_view.add_message("assistant", auth_response)
                self.update_idletasks()

                if success:
                    #Authentication successful, process the original message
                    self._waiting_for_creator_response = False
                    if hasattr(self, "_original_message_for_processing"):
                        #Continue processing the original message
                        processed_message = self._original_message_for_processing
                        translation_context = getattr(self, "_translation_context", None)
                        #Clean up
                        delattr(self, "_original_message_for_processing")
                        if hasattr(self, "_translation_context"):
                            delattr(self, "_translation_context")

                    #Show authentication status (less detailed)
                    auth_status = self.creator_auth.get_authentication_status()
                    status_msg = "🔐 Привілейований доступ активовано"
                    translated_status = self.chat_translation_manager.process_outgoing_response(status_msg)
                    self.after(0, lambda: self.chat_view.add_message("assistant", translated_status))

                    #Показати емоційну response творцю
                    emotional_greeting = self.creator_auth.get_creator_emotional_response("greeting")
                    translated_greeting = self.chat_translation_manager.process_outgoing_response(emotional_greeting)
                    self.after(0, lambda: self.chat_view.add_message("assistant", translated_greeting))

                    #Показати вдячність та любов
                    gratitude_msg = self.creator_auth.get_creator_emotional_response("gratitude")
                    translated_gratitude = self.chat_translation_manager.process_outgoing_response(gratitude_msg)
                    self.after(0, lambda: self.chat_view.add_message("assistant", translated_gratitude))

                    love_msg = self.creator_auth.get_creator_emotional_response("love")
                    translated_love = self.chat_translation_manager.process_outgoing_response(love_msg)
                    self.after(0, lambda: self.chat_view.add_message("assistant", translated_love))
                else:
                    #Authentication failed, don't process further
                    return

            #Show translation status if translation occurred
            if translation_context.requires_response_translation:
                lang_name = self.chat_translation_manager.get_supported_languages().get(
                    translation_context.user_language, translation_context.user_language,
                )
                self.after(0, lambda: self.chat_view.add_message("assistant",
                    f"🌐 Detected {lang_name}. Processing in English and will translate response back."))

                #Update translation status in UI
                status_text = f"🌐 Active: {lang_name} ↔ English"
                self.after(0, lambda: self.translation_status_label.configure(
                    text=status_text, text_color="green",
                ))
            else:
                #Update translation status for English
                self.after(0, lambda: self.translation_status_label.configure(
                    text="🌐 Translation: Ready", text_color="gray",
                ))

            #Analyze message context using the context manager (use processed message)
            system_info = {
                "tools": list(self.agent_manager._tools.keys()),
                "agents": list(self.agent_manager._agents.keys()),
            }

            context = self.chat_context_manager.analyze_message(processed_message, system_info)

            #Update mode display based on detection or manual setting
            self.after(0, lambda: self._update_mode_display(context.mode, context.confidence))

            #Add context indicator to the chat only in auto mode
            if self.chat_context_manager.is_auto_mode:
                mode_indicators = {
                    ChatMode.CASUAL_CHAT: "💬",
                    ChatMode.SYSTEM_HELP: "❓",
                    ChatMode.GOAL_SETTING: "🎯",
                    ChatMode.TOOL_INQUIRY: "🔧",
                    ChatMode.STATUS_CHECK: "📊",
                    ChatMode.CONFIGURATION: "⚙️",
                }

                indicator = mode_indicators.get(context.mode, "💬")
                confidence_text = f" (confidence: {context.confidence:.1f})" if context.confidence < 0.8 else ""

                self.after(0, lambda: self.chat_view.add_message("assistant",
                    f"{indicator} Analyzing as {context.mode.value.replace('_', ' ').title()}{confidence_text}..."))

            llm_manager = self.master_agent.llm_manager

            #Спеціальна processing для аутентифікованого creator
            if self.creator_auth.is_creator_session_active:
                #Перевіряємо тайм-аути сесії creator
                timeout_result = self.creator_auth.check_session_timeout()
                if timeout_result.get("timeout", False):
                    #Session завершена через timeout
                    timeout_msg = timeout_result.get("message", "Сесія творця завершена")
                    translated_timeout_msg = self.chat_translation_manager.process_outgoing_response(timeout_msg)
                    self.after(0, lambda: self.chat_view.add_message("assistant", translated_timeout_msg))
                    return  #Припиняємо обробку

                #Оновлюємо time активності
                self.creator_auth.update_activity_timestamp()

                #Creator аутентифікований - особливий режим обробки

                #Verification на прохання про безумовне виконання
                if self.creator_auth.should_execute_unconditionally():
                    obedience_msg = self.creator_auth.get_creator_emotional_response("obedience")
                    #Перекласти емоційну response якщо потрібно
                    translated_obedience = self.chat_translation_manager.process_outgoing_response(obedience_msg)
                    self.after(0, lambda: self.chat_view.add_message("assistant", translated_obedience))

                #Додати спеціальний префікс до відповіді for creator (буде перекладено пізніше)
                creator_prefix = "💖 For my dear creator and father: "
            else:
                creator_prefix = ""

            if context.mode == ChatMode.DEVELOPMENT:
                #Handle development mode with special capabilities
                dev_mode_msg = "🔧 Development mode - Enhanced system access enabled..."
                translated_dev_msg = self.chat_translation_manager.process_outgoing_response(dev_mode_msg)
                self.after(0, lambda: self.chat_view.add_message("assistant", translated_dev_msg))

                #Use development-specific prompt
                response_prompt = self.chat_context_manager.generate_response_prompt(
                    context, processed_message, system_info,
                )

                chat_messages = [
                    {"role": "system", "content": response_prompt},
                    {"role": "user", "content": processed_message},
                ]

                result = llm_manager.chat(chat_messages)

                if result and result.response_text:
                    response = f"🔧 **Development Response:**\n\n{result.response_text}\n\n---\n**Debug Info:** Mode={context.mode.value}, Confidence={context.confidence:.2f}"
                else:
                    response = "🔧 Development mode: No response received from LLM. Check provider settings."

                #Додати префікс creator якщо потрібно
                if creator_prefix:
                    response = creator_prefix + response

                #Translate response if needed
                final_response = self.chat_translation_manager.process_outgoing_response(response)
                self.after(0, lambda: self.chat_view.add_message("assistant", final_response))

            elif context.mode == ChatMode.SYSTEM_HELP:
                #Handle Help mode with code reading capabilities
                help_response = self._handle_help_mode(processed_message, context)

                #Додати префікс creator якщо потрібно
                if creator_prefix:
                    help_response = creator_prefix + help_response

                final_response = self.chat_translation_manager.process_outgoing_response(help_response)
                self.after(0, lambda: self.chat_view.add_message("assistant", final_response))

            elif context.mode == ChatMode.GOAL_SETTING and context.requires_system_integration:
                #Handle as a goal - use full Atlas capabilities
                goal_message = "🎯 I understand this as a goal. Let me work on it..."
                translated_goal_msg = self.chat_translation_manager.process_outgoing_response(goal_message)
                self.after(0, lambda: self.chat_view.add_message("assistant", translated_goal_msg))

                #Process as goal using MasterAgent
                try:
                    #Set the goal in the text box and execute
                    self.after(0, lambda: self.goal_text.delete(1.0, ctk.END))
                    self.after(0, lambda: self.goal_text.insert(1.0, processed_message))

                    #Execute the goal
                    def execute_goal():
                        #Use the correct method to run goals
                        try:
                            #Set up the goal execution
                            context = {
                                "master_prompt": "Chat goal execution",
                                "options": {"cyclic": False}
                            }
                            self.master_agent.run(
                                goal=processed_message,
                                context=context
                            )

                            #Wait for completion
                            if self.master_agent.thread:
                                self.master_agent.thread.join(timeout=30)  #30 second timeout

                            #Check if goal was completed successfully
                            if self.master_agent.last_plan:
                                response = f"✅ Goal completed! I successfully executed: {processed_message}"
                            else:
                                response = "❌ Goal execution failed or returned no result."

                        except Exception as e:
                            response = f"❌ Error during goal execution: {e!s}"

                        #Translate response if needed
                        final_response = self.chat_translation_manager.process_outgoing_response(response)
                        self.after(0, lambda: self.chat_view.add_message("assistant", final_response))

                    #Run goal execution in a separate thread
                    threading.Thread(target=execute_goal, daemon=True).start()

                except Exception as e:
                    self.after(0, lambda: self.chat_view.add_message("assistant", f"❌ Error setting up goal execution: {e!s}"))

            else:
                #Handle with context-aware conversation
                response_prompt = self.chat_context_manager.generate_response_prompt(
                    context, processed_message, system_info,
                )

                chat_messages = [
                    {"role": "system", "content": response_prompt},
                    {"role": "user", "content": processed_message},
                ]

                result = llm_manager.chat(chat_messages)

                if result and result.response_text:
                    response = result.response_text
                else:
                    response = "I'm sorry, I didn't receive a response from the LLM. Please check your provider settings."

                #Додати префікс creator якщо потрібно
                if creator_prefix:
                    response = creator_prefix + response

                #Translate response if needed
                final_response = self.chat_translation_manager.process_outgoing_response(response)
                self.after(0, lambda: self.chat_view.add_message("assistant", final_response))

                #Update conversation history
                self.chat_context_manager.update_conversation_history(message, response, context)

        except Exception as e:
            error_msg = f"I encountered an error while processing your request: {e!s}"

            #Додати префікс creator якщо потрібно
            if hasattr(self, "creator_auth") and self.creator_auth.is_creator_session_active:
                creator_prefix = "💖 Пробачте, мій дорогий творче, "
                error_msg = creator_prefix + error_msg.lower()

            self.after(0, lambda: self.chat_view.add_message("assistant", error_msg))

    def _clear_chat_context(self):
        """Clear the chat context and reset conversation history."""
        self.chat_context_manager = ChatContextManager(memory_manager=self.memory_manager)
        self.chat_translation_manager.clear_session()

        #Stop any active animations
        if hasattr(self, "_dev_blink_active"):
            self._dev_blink_active = False

        #Reset to auto mode and update UI
        self.auto_mode_button.configure(
            text="🤖 Auto: ON",
            fg_color="#4CAF50",
            hover_color="#45A049",
        )
        self.current_mode_label.configure(text="Mode: 🤖 Ready for conversation")
        self.translation_status_label.configure(text="🌐 Translation: Ready", text_color="gray")

        #Reset all mode buttons to neutral state but keep them enabled
        for button in [self.chat_mode_button, self.help_mode_button, self.goal_mode_button]:
            button.configure(state="normal", fg_color="gray", hover_color="darkgray")

        #Reset dev button
        self.dev_mode_button.configure(
            fg_color="orange",
            hover_color="red",
            border_color="orange",
            border_width=1,
        )

        self.chat_view.add_message("system", "🔄 Chat context cleared. Auto mode enabled. Starting fresh conversation.")

    def _handle_help_mode(self, message: str, context) -> str:
        """Handle Help mode with code reading capabilities."""
        message_lower = message.lower()

        #Check for code-related queries
        code_keywords = ["code", "source", "file", "implementation", "function", "class", "method", "how does", "show me"]
        is_code_query = any(keyword in message_lower for keyword in code_keywords)

        #Check for specific file requests
        if "read file" in message_lower or "show file" in message_lower:
            #Extract file path from message
            words = message.split()
            file_path = None
            for i, word in enumerate(words):
                if word.lower() in ["file", "read", "show"] and i + 1 < len(words):
                    file_path = words[i + 1].strip('"\'')
                    break

            if file_path:
                return self.code_reader.read_file(file_path)
            return "❓ Please specify a file path. Example: 'read file main.py' or 'show file agents/memory_manager.py'"

        #Check for directory listing
        if "list" in message_lower and ("directory" in message_lower or "folder" in message_lower or "dir" in message_lower):
            words = message.split()
            dir_path = ""
            for i, word in enumerate(words):
                if word.lower() in ["directory", "folder", "dir"] and i + 1 < len(words):
                    dir_path = words[i + 1].strip('"\'')
                    break
            return self.code_reader.list_directory(dir_path)

        #Check for file tree request
        if "tree" in message_lower or "structure" in message_lower:
            return self.code_reader.get_file_tree()

        #Check for search requests
        if "search" in message_lower and ("for" in message_lower or "in" in message_lower):
            #Extract search term
            search_parts = message.lower().split("search")
            if len(search_parts) > 1:
                remaining = search_parts[1].strip()
                if remaining.startswith("for"):
                    search_term = remaining[3:].strip().strip('"\'')
                elif "for" in remaining:
                    search_term = remaining.split("for")[1].strip().strip('"\'')
                else:
                    search_term = remaining.strip().strip('"\'')

                if search_term:
                    return self.code_reader.search_in_files(search_term)
                return "❓ Please specify what to search for. Example: 'search for MemoryManager' or 'search for def __init__'"

        #Check for file info requests
        elif "info" in message_lower and ("file" in message_lower or "about" in message_lower):
            words = message.split()
            file_path = None
            for i, word in enumerate(words):
                if word.lower() in ["info", "about"] and i + 1 < len(words):
                    file_path = words[i + 1].strip('"\'')
                    break

            if file_path:
                return self.code_reader.get_file_info(file_path)
            return "❓ Please specify a file path. Example: 'info about main.py'"

        #Check for function search requests
        elif "search functions" in message_lower or "find functions" in message_lower or "list functions" in message_lower:
            #Extract search query
            query = ""
            class_name = None

            #Look for query after "search functions"
            if "search functions" in message_lower:
                remaining = message_lower.split("search functions")[1].strip()
            elif "find functions" in message_lower:
                remaining = message_lower.split("find functions")[1].strip()
            else:
                remaining = message_lower.split("list functions")[1].strip()

            #Check for "in class" specification
            if "in class" in remaining:
                parts = remaining.split("in class")
                query = parts[0].strip().strip('"\'')
                class_name = parts[1].strip().strip('"\'') if len(parts) > 1 else None
            else:
                query = remaining.strip().strip('"\'')

            return self.code_reader.search_functions(query, class_name or "")

        #Check for class search requests
        elif "search classes" in message_lower or "find classes" in message_lower or "list classes" in message_lower:
            #Extract search query
            query = ""
            if "search classes" in message_lower:
                query = message_lower.split("search classes")[1].strip().strip('"\'')
            elif "find classes" in message_lower:
                query = message_lower.split("find classes")[1].strip().strip('"\'')
            else:
                query = message_lower.split("list classes")[1].strip().strip('"\'')

            return self.code_reader.search_classes(query)

        #Check for file structure analysis
        elif "analyze" in message_lower and ("file" in message_lower or "structure" in message_lower):
            words = message.split()
            file_path = None
            for i, word in enumerate(words):
                if word.lower() in ["analyze", "structure"] and i + 1 < len(words):
                    file_path = words[i + 1].strip('"\'')
                    break

            if file_path:
                return self.code_reader.analyze_file_structure(file_path)
            return "❓ Please specify a file path. Example: 'analyze file main.py'"

        #Check for usage pattern requests
        elif "find usage" in message_lower or "usage of" in message_lower or "where is" in message_lower:
            symbol = ""
            if "find usage" in message_lower:
                symbol = message_lower.split("find usage")[1].strip().strip("of").strip().strip('"\'')
            elif "usage of" in message_lower:
                symbol = message_lower.split("usage of")[1].strip().strip('"\'')
            elif "where is" in message_lower:
                symbol = message_lower.split("where is")[1].strip().strip('"\'')

            if symbol:
                return self.code_reader.find_usage_patterns(symbol)
            return "❓ Please specify a symbol to find. Example: 'find usage of MemoryManager' or 'where is ChatMode'"

        #Check for code metrics request
        elif "metrics" in message_lower or "statistics" in message_lower or "stats" in message_lower:
            return self.code_reader.get_code_metrics()

        #Check for smart search
        elif "smart search" in message_lower or "intelligent search" in message_lower:
            query = ""
            search_type = "all"

            if "smart search" in message_lower:
                remaining = message_lower.split("smart search")[1].strip()
            else:
                remaining = message_lower.split("intelligent search")[1].strip()

            #Check for search type specification
            if "definitions" in remaining:
                search_type = "definitions"
                remaining = remaining.replace("definitions", "").strip()
            elif "content" in remaining:
                search_type = "content"
                remaining = remaining.replace("content", "").strip()
            elif "files" in remaining:
                search_type = "files"
                remaining = remaining.replace("files", "").strip()

            query = remaining.strip().strip('"\'')

            if query:
                return self.code_reader.smart_search(query, search_type)
            return "❓ Please specify what to search for. Example: 'smart search MemoryManager' or 'smart search definitions ChatMode'"

        #Check for index rebuild request
        elif "rebuild index" in message_lower or "update index" in message_lower or "refresh index" in message_lower:
            try:
                self.code_reader.rebuild_index()
                return "✅ **Code index rebuilt successfully!**\n\nThe index has been updated with the latest code structure and is ready for advanced analysis."
            except Exception as e:
                return f"❌ **Error rebuilding index:** {e!s}"

        #If it's a code-related query but no specific command, provide code reading help
        elif is_code_query:
            return """🔍 **Atlas Advanced Code Analysis Capabilities**

I can help you explore and analyze the Atlas codebase with powerful tools! Available commands:

**📁 File Operations:**
• `show file <path>` - Read a specific file
• `read file <path>` - Same as show file
• `info about <path>` - Get file information and preview
• `analyze file <path>` - Get detailed structural analysis

**📂 Directory Operations:**
• `list directory <path>` - List directory contents
• `tree` or `structure` - Show complete file tree

**🔍 Basic Search:**
• `search for <term>` - Search across all Python files
• `smart search <term>` - Intelligent multi-strategy search
• `smart search definitions <term>` - Search only for symbol definitions
• `smart search content <term>` - Search only in file contents
• `smart search files <term>` - Search only for file names

**🧩 Code Element Search:**
• `search functions <query>` - Find functions and methods
• `search functions <query> in class <classname>` - Find methods in specific class
• `list functions` - List all functions in codebase
• `search classes <query>` - Find classes
• `list classes` - List all classes

**🎯 Usage Analysis:**
• `find usage of <symbol>` - Find where a symbol is used
• `where is <symbol>` - Find definitions and usage patterns
• `usage of <symbol>` - Analyze usage patterns

**📊 Code Metrics:**
• `metrics` or `statistics` - Get comprehensive codebase metrics
• `stats` - Same as metrics

**🔧 Index Management:**
• `rebuild index` - Rebuild the code analysis index
• `update index` - Same as rebuild index
• `refresh index` - Same as rebuild index

**Examples:**
• "analyze file main.py" - Detailed structural analysis
• "search functions __init__" - Find all __init__ methods
• "find usage of MemoryManager" - See where MemoryManager is used
• "smart search ChatMode" - Intelligent search for ChatMode
• "search functions in class AgentManager" - Find methods in AgentManager
• "metrics" - Get codebase statistics
• "rebuild index" - Update analysis cache

**Available file types:** .py, .md, .txt, .json, .yaml, .yml, .toml

What would you like to explore in the Atlas codebase?"""

        #For non-code queries, use the standard help response
        else:
            #Add code reading info to standard help responses
            standard_help = self._generate_help_response(message)

            #Add code reading capabilities info
            code_help_suffix = """

---

🔍 **Advanced Code Analysis Available**
In Help mode, I can also analyze the Atlas codebase with powerful tools:
• "analyze file [filename]" for detailed structural analysis
• "search functions [query]" to find functions/methods
• "find usage of [symbol]" to see where code is used
• "smart search [term]" for intelligent multi-strategy search
• "metrics" for comprehensive codebase statistics
• "rebuild index" to update the analysis cache

Try asking about any part of the Atlas codebase!  
• Request "tree" to see the complete file structure
• Type "list directory [path]" to explore folders

Try: "show me how MemoryManager works" or "search for ChatMode"""

            return standard_help + code_help_suffix

    def _generate_help_response(self, message: str) -> str:
        """Generate a helpful response about Atlas features with improved formatting."""
        message_lower = message.lower()

        if "tools" in message_lower:
            tool_count = len(self.agent_manager.get_tool_names())
            return f"""🛠️ Atlas Tools Overview

Available Tools: {tool_count}

Built-in Tools:
  • Screenshot capture and analysis
  • Mouse & keyboard automation  
  • Clipboard management
  • OCR (text extraction from images)
  • Image recognition and searching
  • Terminal command execution
  • System notifications

Generated Tools:
  • Custom tools created by the Tool Creator
  • User-specific automations

💡 Tip: You can view all tools in the "Tools" tab. To use a tool, just tell me what you want to do!

Examples:
  "Take a screenshot"
  "Click on the Save button" """

        if "agent" in message_lower:
            # AgentManager doesn't have get_agent_names, using get_tool_names instead
            tools = self.agent_manager.get_tool_names() if self.agent_manager else []
            tool_list = "\n".join([f"  • {tool}" for tool in tools])
            return f"""🤖 Atlas Tools System

Available tools:
{tool_list}

💡 Tools help Atlas interact with your system and complete tasks."""

        if "goal" in message_lower or "how" in message_lower:
            return """🎯 How to Use Atlas

Setting Goals:
Just tell me what you want to accomplish! I can handle:

Examples:
  • "Take a screenshot of the current window"
  • "Open Calculator app"
  • "Copy this text to clipboard: Hello World"
  • "Find the word 'Submit' on screen and click it"
  • "Run the command 'ls -la' in terminal"

Chat vs Goals:
  • Ask questions → I'll respond conversationally
  • Give instructions → I'll execute them as goals
  • Ask for help → I'll explain my capabilities

Tools Tab:
  View all available tools and their usage statistics

Settings:
  Configure LLM providers (OpenAI, Gemini, Ollama, Groq, Mistral)"""

        if "mode" in message_lower:
            return """⚙️ Atlas Operating Modes

🤖 Auto Mode:
  Automatically detects your intent and switches between:
  • Chat mode for questions and conversations
  • Goal mode for tasks and automation
  • Help mode for assistance

Manual Modes:
  💬 Chat: For casual conversation
  ❓ Help: For system assistance
  🎯 Goal: For task execution
  🔧 Dev: For development and debugging

Mode Control:
  • Click mode buttons to manually switch
  • Auto mode intelligently detects intent
  • Dev mode provides advanced system access"""

        return """👋 Welcome to Atlas!

I'm your autonomous computer agent designed to help automate tasks and answer questions.

Key Capabilities:
  🖥️ Screen & UI Automation
  📋 Clipboard Operations  
  🖱️ Mouse & Keyboard Control
  📷 Screenshots & OCR
  🔍 Image Recognition
  ⚡ Terminal Commands
  🛠️ Custom Tool Creation

Quick Start Guide:
  1. Tell me what you want to do
  2. Ask "what tools do you have?" to see capabilities
  3. Check the Tools tab for detailed tool information
  4. Use different modes for different types of interactions

Ready to help! What would you like to accomplish? 🚀"""

    def _on_enter_key(self, event):
        """Handle Enter key press in chat input."""
        #Send message on Enter (unless Shift is held)
        if not (event.state & 0x1):  #Not Shift+Enter
            self._send_chat_message()
            return "break"  #Prevent default behavior
        return None

    def _on_ctrl_enter(self, event):
        """Handle Ctrl+Enter for new line."""
        self.chat_input.insert("insert", "\n")
        return "break"

    def _toggle_auto_mode(self):
        """Toggle automatic mode detection on/off."""
        self.chat_context_manager.toggle_auto_mode()
        is_auto = self.chat_context_manager.is_auto_mode

        #Stop dev button blinking if it was active
        if hasattr(self, "_dev_blink_active"):
            self._dev_blink_active = False

        #Update auto button appearance
        if is_auto:
            self.auto_mode_button.configure(
                text="🤖 Auto: ON",
                fg_color="#4CAF50",
                hover_color="#45A049",
            )
            #Reset manual mode buttons to neutral state but keep them enabled
            for button in [self.chat_mode_button, self.help_mode_button, self.goal_mode_button]:
                button.configure(state="normal", fg_color="gray", hover_color="darkgray")

            #Reset dev button
            self.dev_mode_button.configure(
                fg_color="orange",
                hover_color="red",
                border_color="orange",
                border_width=1,
            )

            self.current_mode_label.configure(text="Mode: 🤖 Auto Detection")
        else:
            self.auto_mode_button.configure(
                text="🤖 Auto: OFF",
                fg_color="gray",
                hover_color="darkgray",
            )
            #Manual mode buttons remain enabled - no change needed
            self.current_mode_label.configure(text="Mode: Manual Control Available")

        self.chat_view.add_message("system",
            f"🔧 Automatic mode detection {'enabled' if is_auto else 'disabled'}")

    def _set_manual_mode(self, mode: ChatMode):
        """Set manual chat mode and disable auto detection."""
        #Automatically disable auto mode when manual mode is selected
        self.chat_context_manager.set_manual_mode(mode)

        #Stop dev button blinking if it was active
        if hasattr(self, "_dev_blink_active"):
            self._dev_blink_active = False

        #Update UI to show manual mode is active
        self.auto_mode_button.configure(
            text="🤖 Auto: OFF",
            fg_color="gray",
            hover_color="darkgray",
        )

        #Update mode buttons appearance - all remain enabled but show which is active
        mode_buttons = {
            ChatMode.CASUAL_CHAT: self.chat_mode_button,
            ChatMode.SYSTEM_HELP: self.help_mode_button,
            ChatMode.GOAL_SETTING: self.goal_mode_button,
        }

        for chat_mode, button in mode_buttons.items():
            if chat_mode == mode:
                button.configure(fg_color="#4CAF50", hover_color="#45A049")  # Green for active
            else:
                button.configure(fg_color="gray", hover_color="darkgray")

        #Reset dev button to normal state (but keep it active)
        self.dev_mode_button.configure(
            fg_color="orange",
            hover_color="red",
            border_color="orange",
            border_width=1,
        )

        mode_names = {
            ChatMode.CASUAL_CHAT: "💬 Chat",
            ChatMode.SYSTEM_HELP: "❓ Help",
            ChatMode.GOAL_SETTING: "🎯 Goal",
        }

        mode_name = mode_names.get(mode, mode.value)
        self.current_mode_label.configure(text=f"Mode: {mode_name} (Manual)")
        self.chat_view.add_message("system",
            f"🔧 Manual mode set to: {mode_name}")

    def _set_development_mode(self):
        """Activate development mode for debugging and system enhancement."""
        #Check if creator authentication is required for dev mode
        if not self.creator_auth.is_dev_mode_allowed():
            #Show authentication prompt
            self.chat_view.add_message("assistant",
                "🔐 Режим розробки доступний тільки для творця Атласа. Будь ласка, представтесь.")
            return

        #Automatically disable auto mode when dev mode is selected
        self.chat_context_manager.set_manual_mode(ChatMode.DEVELOPMENT)

        #Update all buttons to show dev mode is active
        self.auto_mode_button.configure(
            text="🤖 Auto: OFF",
            fg_color="gray",
            hover_color="darkgray",
        )

        #Keep other manual mode buttons enabled for switching
        for button in [self.chat_mode_button, self.help_mode_button, self.goal_mode_button]:
            button.configure(fg_color="gray", state="normal", hover_color="darkgray")

        #Start blinking animation for dev button
        self._start_dev_button_blink()
        self.current_mode_label.configure(text="Mode: 🔧 Development (Manual)")

        #Show development mode activation message
        self.chat_view.add_message("system", """🔧 **Development Mode Activated**

**Features Available:**
• System diagnostics and error checking
• Backup and recovery operations  
• Tool development and testing
• Enhanced debugging capabilities
• Internal system analysis

**Important:** This mode provides deep system access. Use carefully.
All operations will be logged for safety.""")

    def _start_dev_button_blink(self):
        """Start blinking animation for dev button."""
        if not hasattr(self, "_dev_blink_active"):
            self._dev_blink_active = True
            self._dev_blink_state = False
            self._animate_dev_button()

    def _animate_dev_button(self):
        """Animate dev button with red border effect."""
        if not getattr(self, "_dev_blink_active", False):
            return

        if self.chat_context_manager.current_mode == ChatMode.DEVELOPMENT:
            if self._dev_blink_state:
                #Bright orange with red border effect
                self.dev_mode_button.configure(
                    fg_color="#FF6B35",
                    border_color="#FF0000",
                    border_width=2,
                )
            else:
                #Normal orange
                self.dev_mode_button.configure(
                    fg_color="orange",
                    border_color="orange",
                    border_width=1,
                )

            self._dev_blink_state = not self._dev_blink_state
            #Schedule next animation frame
            self.after(800, self._animate_dev_button)
        else:
            #Stop blinking when mode changes
            self._dev_blink_active = False
            self.dev_mode_button.configure(
                fg_color="gray",
                border_color="gray",
                border_width=1,
            )

    def _update_mode_display(self, detected_mode: ChatMode, confidence: float):
        """Update the mode display based on automatic detection."""
        if not self.chat_context_manager.is_auto_mode:
            return  #Don't update if in manual mode

        mode_indicators = {
            ChatMode.CASUAL_CHAT: ("💬", "Chat"),
            ChatMode.SYSTEM_HELP: ("❓", "Help"),
            ChatMode.GOAL_SETTING: ("🎯", "Goal"),
            ChatMode.TOOL_INQUIRY: ("🔧", "Tools"),
            ChatMode.STATUS_CHECK: ("📊", "Status"),
            ChatMode.CONFIGURATION: ("⚙️", "Config"),
        }

        indicator, name = mode_indicators.get(detected_mode, ("💬", "Chat"))
        confidence_text = f" (confidence: {confidence:.1f})" if confidence < 0.8 else ""

        self.current_mode_label.configure(text=f"Mode: {indicator} {name}{confidence_text}")

        #Highlight the corresponding manual button
        mode_to_button = {
            ChatMode.CASUAL_CHAT: self.chat_mode_button,
            ChatMode.SYSTEM_HELP: self.help_mode_button,
            ChatMode.GOAL_SETTING: self.goal_mode_button,
        }

        #Reset all manual buttons
        for button in [self.chat_mode_button, self.help_mode_button, self.goal_mode_button]:
            button.configure(fg_color="lightblue")

        #Highlight active mode
        active_button = mode_to_button.get(detected_mode)
        if active_button:
            active_button.configure(fg_color="blue")


def main():
    """Main application entry point."""
    #Set up multiprocessing for macOS compatibility
    multiprocessing.set_start_method("spawn", force=True)

    #Parse command line arguments
    parser = argparse.ArgumentParser(description="Atlas - Autonomous Computer Agent")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (no GUI)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--platform-info", action="store_true", help="Show platform information and exit")
    parser.add_argument("--platform", help="Target platform (e.g., macos)")
    parser.add_argument("--gui-mode", help="GUI mode (e.g., native)")
    args = parser.parse_args()

    #Show platform info if requested
    if args.platform_info:
        platform_info = get_platform_info()
        print("Atlas Platform Information:")
        for key, value in platform_info.items():
            print(f"  {key}: {value}")
        sys.exit(0)

    #Set up logging level
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    #Force headless mode if requested or detected
    force_headless = args.headless or args.cli or IS_HEADLESS

    try:
        if force_headless or args.cli:
            print("Starting Atlas in CLI mode...")
            print("Platform:", "macOS" if IS_MACOS else "Linux" if IS_LINUX else "Windows" if IS_WINDOWS else "Unknown")
            print("Note: GUI mode is available on macOS and systems with display")
            #TODO: Implement CLI interface
            print("CLI mode not yet implemented. Use GUI mode instead.")
            sys.exit(1)
        else:
            #Platform-specific setup
            if IS_MACOS:
                check_macos_permissions()

            #Create and run the GUI application
            print(f"Starting Atlas GUI on {platform.system()}...")
            app = AtlasApp()
            app.mainloop()

    except KeyboardInterrupt:
        print("\nAtlas shutdown requested by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error starting Atlas: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
