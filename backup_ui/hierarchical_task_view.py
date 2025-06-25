"""
Hierarchical Task View for Atlas

This module provides a UI component for displaying and managing the three-level
hierarchical task structure in the Atlas interface.
"""

from typing import Any, Dict, Optional, Callable
import customtkinter as ctk
from datetime import datetime
import threading
import queue
import time

from utils.logger import get_logger


class HierarchicalTaskView(ctk.CTkFrame):
    """
    UI component for displaying and managing hierarchical tasks.
    
    Features:
    - Tree view of strategic, tactical, and operational tasks
    - Task status indicators with progress bars
    - Tool and plugin assignment interface
    - Task control buttons (pause, resume, cancel)
    - Real-time status updates
    - Asynchronous UI updates to prevent blocking
    """
    
    def __init__(self, master, task_callback: Optional[Callable[[str, str, Any], None]] = None):
        """
        Initialize the hierarchical task view.
        
        Args:
            master: Parent widget
            task_callback: Callback for task actions (action, task_id, data)
        """
        print("[LOG] HierarchicalTaskView: __init__ called")
        super().__init__(master)
        self.task_callback = task_callback
        self.logger = get_logger(self.__class__.__name__)
        
        # Task storage
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.root_task_id: Optional[str] = None
        
        # UI components
        self.task_tree = None
        self.task_details_frame = None
        self.task_controls_frame = None
        self.task_frames = {}  # Store references to task frames
        
        # Async update queue and state
        self.update_queue = queue.Queue()
        self.is_updating = False
        self.update_thread = None
        
        # Progress indicator
        self.progress_label = None
        
        self._create_widgets()
        self._start_async_updates()
        
    def _create_widgets(self):
        """Create the UI widgets."""
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Task tree
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Tree header (simplified without problematic button)
        tree_header = ctk.CTkLabel(left_panel, text="Hierarchical Task Structure", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        tree_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Progress indicator
        self.progress_label = ctk.CTkLabel(left_panel, text="", 
                                         font=ctk.CTkFont(size=10), text_color="gray")
        self.progress_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="e")
        
        # Task tree (using scrollable frame with custom tree-like structure)
        self.task_tree = ctk.CTkScrollableFrame(left_panel, label_text="Tasks", height=400)
        self.task_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Right panel - Task details and controls
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Details header
        details_header = ctk.CTkLabel(right_panel, text="Task Details", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        details_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Task details frame
        self.task_details_frame = ctk.CTkScrollableFrame(right_panel, label_text="Information", height=300)
        self.task_details_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Task controls frame
        self.task_controls_frame = ctk.CTkFrame(right_panel)
        self.task_controls_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Initially show no task selected
        self._show_no_task_selected()
        
    def _start_async_updates(self):
        """Start the asynchronous update loop."""
        def update_loop():
            while True:
                try:
                    # Get update from queue with timeout
                    update_data = self.update_queue.get(timeout=0.1)
                    
                    # Schedule UI update on main thread
                    self.after(0, self._process_ui_update, update_data)
                    
                except queue.Empty:
                    # No updates, continue loop
                    continue
                except Exception as e:
                    self.logger.error(f"Error in update loop: {e}")
                    time.sleep(0.1)
        
        # Start update thread
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
        
    def _process_ui_update(self, update_data: Dict[str, Any]):
        """Process UI update on main thread."""
        try:
            update_type = update_data.get("type")
            
            if update_type == "progress":
                # Update progress indicator
                progress_text = update_data.get("text", "")
                if self.progress_label:
                    self.progress_label.configure(text=progress_text)
                    
            elif update_type == "task_frame":
                # Add task frame to UI
                task_frame_data = update_data.get("data")
                self._add_task_frame_to_ui(task_frame_data)
                
            elif update_type == "clear_tree":
                # Clear task tree
                for widget in self.task_tree.winfo_children():
                    widget.destroy()
                self.task_frames.clear()
                
            elif update_type == "scroll":
                # Scroll to bottom
                self._simple_scroll_to_bottom()
                
        except Exception as e:
            self.logger.error(f"Error processing UI update: {e}")
            
    def _add_task_frame_to_ui(self, task_frame_data: Dict[str, Any]):
        """Add task frame to UI on main thread."""
        try:
            task_id = task_frame_data["task_id"]
            level = task_frame_data["level"]
            task = task_frame_data["task"]
            
            # Create task frame
            task_frame = ctk.CTkFrame(self.task_tree, height=40)
            task_frame.pack(fill="x", padx=(level * 20, 5), pady=1)
            task_frame.grid_columnconfigure(1, weight=1)
            
            # Status indicator
            status_color = self._get_status_color(task.get("status", "pending"))
            status_label = ctk.CTkLabel(task_frame, text="●", text_color=status_color, 
                                      font=ctk.CTkFont(size=16))
            status_label.grid(row=0, column=0, padx=(5, 10), pady=5)
            
            # Task title with better formatting
            title_text = task.get("title", "Unknown Task")
            if level == 0:  # Strategic level
                display_text = f"🎯 {title_text}"
            elif level == 1:  # Tactical level
                display_text = f"📋 {title_text}"
            else:  # Operational level
                display_text = f"⚡ {title_text}"
                
            title_label = ctk.CTkLabel(task_frame, text=display_text, 
                                     font=ctk.CTkFont(size=11, weight="bold"))
            title_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Progress bar with percentage
            progress = task.get("progress", 0.0)
            progress_bar = ctk.CTkProgressBar(task_frame, width=80)
            progress_bar.grid(row=0, column=2, padx=5, pady=5)
            progress_bar.set(progress)
            
            # Progress percentage label
            progress_text = f"{progress:.0%}"
            progress_label = ctk.CTkLabel(task_frame, text=progress_text, 
                                        font=ctk.CTkFont(size=10))
            progress_label.grid(row=0, column=3, padx=2, pady=5)
            
            # Level indicator
            level_emoji = self._get_level_emoji(task.get("level", "operational"))
            level_label = ctk.CTkLabel(task_frame, text=level_emoji, 
                                     font=ctk.CTkFont(size=12))
            level_label.grid(row=0, column=4, padx=5, pady=5)
            
            # Bind click event
            task_frame.bind("<Button-1>", lambda e, tid=task_id: self._on_task_click(tid))
            title_label.bind("<Button-1>", lambda e, tid=task_id: self._on_task_click(tid))
            
            # Store reference to task frame
            task_frame.task_id = task_id
            self.task_frames[task_id] = task_frame
            
        except Exception as e:
            self.logger.error(f"Error adding task frame to UI: {e}")
        
    def update_plan(self, plan_data: Dict[str, Any]):
        """
        Update the view with a new hierarchical plan (asynchronous).
        
        Args:
            plan_data: Plan data containing tasks and metadata
        """
        try:
            # Handle different data structures
            if "plan" in plan_data:
                # Old format with nested plan
                plan = plan_data.get("plan", {})
                tasks = plan_data.get("tasks", {})
            else:
                # New format with direct data
                plan = plan_data
                tasks = plan_data.get("tasks", [])
            
            self.root_task_id = plan.get("root_task_id")
            
            # Convert tasks list to dictionary if needed
            if isinstance(tasks, list):
                self.tasks = {task["id"]: task for task in tasks}
            else:
                self.tasks = tasks
            
            # Start async update process
            self._start_async_plan_update(plan)
            
        except Exception as e:
            self.logger.error(f"Failed to update plan: {e}", exc_info=True)
            
    def _start_async_plan_update(self, plan: Dict[str, Any]):
        """Start asynchronous plan update process."""
        def async_update():
            try:
                # Update progress
                self.update_queue.put({
                    "type": "progress",
                    "text": "Clearing tree..."
                })
                
                # Clear tree
                self.update_queue.put({"type": "clear_tree"})
                
                # Build tree structure asynchronously
                if self.root_task_id and self.root_task_id in self.tasks:
                    self._build_task_tree_async(self.root_task_id, 0)
                
                # Update progress
                self.update_queue.put({
                    "type": "progress",
                    "text": f"Loaded {len(self.tasks)} tasks"
                })
                
                # Show plan summary
                self.after(0, lambda: self._show_plan_summary(plan))
                
                # Scroll to bottom
                self.update_queue.put({"type": "scroll"})
                
                # Clear progress after delay
                self.after(2000, lambda: self.update_queue.put({
                    "type": "progress",
                    "text": ""
                }))
                
            except Exception as e:
                self.logger.error(f"Error in async plan update: {e}")
                self.update_queue.put({
                    "type": "progress",
                    "text": f"Error: {str(e)}"
                })
        
        # Start async update in separate thread
        threading.Thread(target=async_update, daemon=True).start()
        
    def _build_task_tree_async(self, task_id: str, level: int):
        """Build task tree asynchronously."""
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        
        # Add task frame to queue
        self.update_queue.put({
            "type": "task_frame",
            "data": {
                "task_id": task_id,
                "level": level,
                "task": task
            }
        })
        
        # Update progress periodically
        if level == 0:  # Only for top-level tasks
            self.update_queue.put({
                "type": "progress",
                "text": f"Building tree... {len(self.task_frames) + 1}/{len(self.tasks)}"
            })
        
        # Add children recursively
        children = task.get("children", [])
        for child_id in children:
            self._build_task_tree_async(child_id, level + 1)
            
        # Small delay to prevent UI blocking
        time.sleep(0.01)
        
    def update_task(self, task_data: Dict[str, Any]):
        """
        Update a specific task in the view.
        
        Args:
            task_data: Updated task data
        """
        try:
            task_id = task_data.get("id")
            if not task_id:
                return
                
            # Update task data
            self.tasks[task_id] = task_data
            
            # Update tree display
            self._update_task_in_tree(task_id)
            
            # Update details if this task is currently selected
            if hasattr(self, '_selected_task_id') and self._selected_task_id == task_id:
                self._show_task_details(task_data)
                
        except Exception as e:
            self.logger.error(f"Failed to update task: {e}", exc_info=True)
            
    def _build_task_tree(self, task_id: str, level: int):
        """
        Build the task tree structure recursively.
        
        Args:
            task_id: ID of the task to add
            level: Indentation level
        """
        if task_id not in self.tasks:
            return
            
        task = self.tasks[task_id]
        
        # Create task frame with better spacing
        task_frame = ctk.CTkFrame(self.task_tree, height=40)
        task_frame.pack(fill="x", padx=(level * 20, 5), pady=1)
        task_frame.grid_columnconfigure(1, weight=1)
        
        # Status indicator
        status_color = self._get_status_color(task.get("status", "pending"))
        status_label = ctk.CTkLabel(task_frame, text="●", text_color=status_color, 
                                  font=ctk.CTkFont(size=16))
        status_label.grid(row=0, column=0, padx=(5, 10), pady=5)
        
        # Task title with better formatting
        title_text = task.get("title", "Unknown Task")
        # Add task ID for better identification
        if level == 0:  # Strategic level
            display_text = f"🎯 {title_text}"
        elif level == 1:  # Tactical level
            display_text = f"📋 {title_text}"
        else:  # Operational level
            display_text = f"⚡ {title_text}"
            
        title_label = ctk.CTkLabel(task_frame, text=display_text, 
                                 font=ctk.CTkFont(size=11, weight="bold"))
        title_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Progress bar with percentage
        progress = task.get("progress", 0.0)
        progress_bar = ctk.CTkProgressBar(task_frame, width=80)
        progress_bar.grid(row=0, column=2, padx=5, pady=5)
        progress_bar.set(progress)
        
        # Progress percentage label
        progress_text = f"{progress:.0%}"
        progress_label = ctk.CTkLabel(task_frame, text=progress_text, 
                                    font=ctk.CTkFont(size=10))
        progress_label.grid(row=0, column=3, padx=2, pady=5)
        
        # Level indicator
        level_emoji = self._get_level_emoji(task.get("level", "operational"))
        level_label = ctk.CTkLabel(task_frame, text=level_emoji, 
                                 font=ctk.CTkFont(size=12))
        level_label.grid(row=0, column=4, padx=5, pady=5)
        
        # Bind click event
        task_frame.bind("<Button-1>", lambda e, tid=task_id: self._on_task_click(tid))
        title_label.bind("<Button-1>", lambda e, tid=task_id: self._on_task_click(tid))
        
        # Store reference to task frame
        task_frame.task_id = task_id
        self.task_frames[task_id] = task_frame
        
        # Add children recursively
        children = task.get("children", [])
        for child_id in children:
            self._build_task_tree(child_id, level + 1)
            
    def _update_task_in_tree(self, task_id: str):
        """Update a specific task in the tree display."""
        if task_id not in self.task_frames:
            return
            
        task_frame = self.task_frames[task_id]
        task = self.tasks[task_id]
        
        # Update status indicator
        status_color = self._get_status_color(task.get("status", "pending"))
        
        # Find status label (first child)
        if task_frame.winfo_children():
            status_label = task_frame.winfo_children()[0]
            if isinstance(status_label, ctk.CTkLabel):
                status_label.configure(text_color=status_color)
        
        # Update progress bar and percentage
        if len(task_frame.winfo_children()) > 2:
            progress_bar = task_frame.winfo_children()[2]
            progress_label = task_frame.winfo_children()[3]
            
            if isinstance(progress_bar, ctk.CTkProgressBar) and isinstance(progress_label, ctk.CTkLabel):
                progress = task.get("progress", 0.0)
                progress_bar.set(progress)
                progress_label.configure(text=f"{progress:.0%}")
                
    def _on_task_click(self, task_id: str):
        """Handle task selection."""
        if task_id in self.tasks:
            self._selected_task_id = task_id
            self._show_task_details(self.tasks[task_id])
            
    def _show_task_details(self, task: Dict[str, Any]):
        """Show details for the selected task."""
        # Clear details frame
        for widget in self.task_details_frame.winfo_children():
            widget.destroy()
            
        # Task title
        title_label = ctk.CTkLabel(self.task_details_frame, text=task.get("title", "Unknown Task"),
                                 font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Task description
        description = task.get("description", "No description available")
        desc_label = ctk.CTkLabel(self.task_details_frame, text=description, 
                                wraplength=300, justify="left")
        desc_label.pack(anchor="w", padx=10, pady=5)
        
        # Status and progress
        status_frame = ctk.CTkFrame(self.task_details_frame)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        status_text = task.get("status", "pending").upper()
        status_color = self._get_status_color(task.get("status", "pending"))
        status_label = ctk.CTkLabel(status_frame, text=f"Status: {status_text}", 
                                  text_color=status_color, font=ctk.CTkFont(weight="bold"))
        status_label.pack(anchor="w", padx=10, pady=5)
        
        progress = task.get("progress", 0.0)
        progress_text = f"Progress: {progress:.1%}"
        progress_label = ctk.CTkLabel(status_frame, text=progress_text)
        progress_label.pack(anchor="w", padx=10, pady=5)
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        progress_bar.pack(padx=10, pady=5)
        progress_bar.set(progress)
        
        # Task metadata
        metadata_frame = ctk.CTkFrame(self.task_details_frame)
        metadata_frame.pack(fill="x", padx=10, pady=5)
        
        # Level
        level = task.get("level", "operational")
        level_emoji = self._get_level_emoji(level)
        level_label = ctk.CTkLabel(metadata_frame, text=f"Level: {level_emoji} {level.title()}")
        level_label.pack(anchor="w", padx=10, pady=5)
        
        # Tools
        tools = task.get("tools", [])
        if tools:
            tools_text = f"Tools: {', '.join(tools)}"
            tools_label = ctk.CTkLabel(metadata_frame, text=tools_text)
            tools_label.pack(anchor="w", padx=10, pady=5)
        
        # Plugins
        plugins = task.get("plugins", [])
        if plugins:
            plugins_text = f"Plugins: {', '.join(plugins)}"
            plugins_label = ctk.CTkLabel(metadata_frame, text=plugins_text)
            plugins_label.pack(anchor="w", padx=10, pady=5)
        
        # Timestamps
        timestamps_frame = ctk.CTkFrame(self.task_details_frame)
        timestamps_frame.pack(fill="x", padx=10, pady=5)
        
        created_at = task.get("created_at")
        if created_at:
            created_time = datetime.fromtimestamp(created_at).strftime("%H:%M:%S")
            created_label = ctk.CTkLabel(timestamps_frame, text=f"Created: {created_time}")
            created_label.pack(anchor="w", padx=10, pady=2)
        
        started_at = task.get("started_at")
        if started_at:
            started_time = datetime.fromtimestamp(started_at).strftime("%H:%M:%S")
            started_label = ctk.CTkLabel(timestamps_frame, text=f"Started: {started_time}")
            started_label.pack(anchor="w", padx=10, pady=2)
        
        completed_at = task.get("completed_at")
        if completed_at:
            completed_time = datetime.fromtimestamp(completed_at).strftime("%H:%M:%S")
            completed_label = ctk.CTkLabel(timestamps_frame, text=f"Completed: {completed_time}")
            completed_label.pack(anchor="w", padx=10, pady=2)
        
        # Error message
        error_message = task.get("error_message")
        if error_message:
            error_frame = ctk.CTkFrame(self.task_details_frame)
            error_frame.pack(fill="x", padx=10, pady=5)
            
            error_label = ctk.CTkLabel(error_frame, text="Error:", 
                                     font=ctk.CTkFont(weight="bold"), text_color="red")
            error_label.pack(anchor="w", padx=10, pady=5)
            
            error_text = ctk.CTkTextbox(error_frame, height=60, width=300)
            error_text.pack(padx=10, pady=5)
            error_text.insert("1.0", error_message)
            error_text.configure(state="disabled")
        
        # Task controls
        self._create_task_controls(task)
        
    def _create_task_controls(self, task: Dict[str, Any]):
        """Create control buttons for the task."""
        # Clear controls frame
        for widget in self.task_controls_frame.winfo_children():
            widget.destroy()
            
        task_id = task.get("id")
        status = task.get("status", "pending")
        
        # Control buttons based on status
        if status == "pending":
            start_btn = ctk.CTkButton(self.task_controls_frame, text="▶ Start", 
                                    command=lambda: self._task_action("start", task_id))
            start_btn.pack(side="left", padx=5, pady=5)
            
        elif status == "running":
            pause_btn = ctk.CTkButton(self.task_controls_frame, text="⏸ Pause", 
                                    command=lambda: self._task_action("pause", task_id))
            pause_btn.pack(side="left", padx=5, pady=5)
            
        elif status == "paused":
            resume_btn = ctk.CTkButton(self.task_controls_frame, text="▶ Resume", 
                                     command=lambda: self._task_action("resume", task_id))
            resume_btn.pack(side="left", padx=5, pady=5)
            
        # Cancel button for active tasks
        if status in ["pending", "running", "paused"]:
            cancel_btn = ctk.CTkButton(self.task_controls_frame, text="❌ Cancel", 
                                     fg_color="red", hover_color="darkred",
                                     command=lambda: self._task_action("cancel", task_id))
            cancel_btn.pack(side="left", padx=5, pady=5)
            
    def _task_action(self, action: str, task_id: str):
        """Handle task action button clicks."""
        if self.task_callback:
            self.task_callback(action, task_id, {})
            
    def _show_no_task_selected(self):
        """Show message when no task is selected."""
        # Clear details frame
        for widget in self.task_details_frame.winfo_children():
            widget.destroy()
            
        no_task_label = ctk.CTkLabel(self.task_details_frame, 
                                   text="Select a task to view details",
                                   font=ctk.CTkFont(size=14))
        no_task_label.pack(pady=20)
        
    def _show_plan_summary(self, plan: Dict[str, Any]):
        """Show plan summary information."""
        # This could be expanded to show plan-level information
        pass
        
    def _get_status_color(self, status: str) -> str:
        """Get color for task status."""
        colors = {
            "pending": "orange",
            "running": "green", 
            "completed": "blue",
            "failed": "red",
            "cancelled": "gray",
            "paused": "yellow"
        }
        return colors.get(status, "gray")
        
    def _get_level_emoji(self, level: str) -> str:
        """Get emoji for task level."""
        emojis = {
            "strategic": "🎯",
            "tactical": "📋", 
            "operational": "⚡"
        }
        return emojis.get(level, "⚡")
        
    def _simple_scroll_to_bottom(self):
        """Simple scroll to bottom without complex canvas operations."""
        try:
            # Simple approach - just update the scrollable frame
            self.task_tree.update_idletasks()
            
            # Try to scroll to bottom using the scrollable frame's method
            if hasattr(self.task_tree, '_parent_canvas'):
                canvas = self.task_tree._parent_canvas
                if canvas:
                    canvas.yview_moveto(1.0)
                    
        except Exception as e:
            # If scrolling fails, just log it and continue
            self.logger.debug(f"Simple scroll failed: {e}")
            # Don't raise the error - just continue normally 