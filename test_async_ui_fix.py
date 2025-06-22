#!/usr/bin/env python3
"""
Test script for async UI updates to prevent blocking
"""

import customtkinter as ctk
import threading
import time
import random
from ui.hierarchical_task_view import HierarchicalTaskView

def create_mock_plan_data(num_tasks=50):
    """Create mock plan data with many tasks to test async loading."""
    tasks = []
    
    # Create strategic tasks
    for i in range(3):
        strategic_task = {
            "id": f"strategic_{i}",
            "title": f"Strategic Task {i+1}",
            "description": f"High-level strategic planning task {i+1}",
            "level": "strategic",
            "status": "pending",
            "progress": 0.0,
            "parent_id": None,
            "children": [],
            "tools": [],
            "plugins": [],
            "metadata": {},
            "created_at": "2024-01-01T10:00:00",
            "started_at": None,
            "completed_at": None,
            "error_message": None
        }
        tasks.append(strategic_task)
        
        # Create tactical tasks for each strategic task
        for j in range(5):
            tactical_task = {
                "id": f"tactical_{i}_{j}",
                "title": f"Tactical Task {i+1}.{j+1}",
                "description": f"Tactical implementation task {i+1}.{j+1}",
                "level": "tactical",
                "status": "pending",
                "progress": 0.0,
                "parent_id": f"strategic_{i}",
                "children": [],
                "tools": [],
                "plugins": [],
                "metadata": {},
                "created_at": "2024-01-01T10:00:00",
                "started_at": None,
                "completed_at": None,
                "error_message": None
            }
            tasks.append(tactical_task)
            strategic_task["children"].append(f"tactical_{i}_{j}")
            
            # Create operational tasks for each tactical task
            for k in range(3):
                operational_task = {
                    "id": f"operational_{i}_{j}_{k}",
                    "title": f"Operational Task {i+1}.{j+1}.{k+1}",
                    "description": f"Detailed operational task {i+1}.{j+1}.{k+1}",
                    "level": "operational",
                    "status": "pending",
                    "progress": 0.0,
                    "parent_id": f"tactical_{i}_{j}",
                    "children": [],
                    "tools": [],
                    "plugins": [],
                    "metadata": {},
                    "created_at": "2024-01-01T10:00:00",
                    "started_at": None,
                    "completed_at": None,
                    "error_message": None
                }
                tasks.append(operational_task)
                tactical_task["children"].append(f"operational_{i}_{j}_{k}")
    
    plan_data = {
        "goal": "Test async UI loading with many tasks",
        "root_task_id": "strategic_0",
        "total_tasks": len(tasks),
        "tasks": tasks
    }
    
    return plan_data

def test_async_loading():
    """Test async loading of hierarchical task view."""
    print("Starting async UI loading test...")
    print("This test will create 45 tasks (3 strategic × 5 tactical × 3 operational)")
    print("The UI should remain responsive during loading...")
    
    # Create main window
    root = ctk.CTk()
    root.title("Async UI Loading Test")
    root.geometry("800x600")
    
    # Create hierarchical task view
    task_view = HierarchicalTaskView(root)
    task_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add control buttons
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(fill="x", padx=10, pady=5)
    
    def load_plan():
        print("Loading plan with many tasks...")
        plan_data = create_mock_plan_data()
        task_view.update_plan(plan_data)
        print("Plan loading started (should be async)")
    
    def load_small_plan():
        print("Loading small plan...")
        small_plan = create_mock_plan_data(9)  # Just 3 strategic tasks
        task_view.update_plan(small_plan)
        print("Small plan loaded")
    
    def clear_plan():
        print("Clearing plan...")
        task_view.update_plan({"tasks": []})
        print("Plan cleared")
    
    # Add buttons
    ctk.CTkButton(control_frame, text="Load Large Plan (45 tasks)", command=load_plan).pack(side="left", padx=5)
    ctk.CTkButton(control_frame, text="Load Small Plan (9 tasks)", command=load_small_plan).pack(side="left", padx=5)
    ctk.CTkButton(control_frame, text="Clear Plan", command=clear_plan).pack(side="left", padx=5)
    
    # Add status label
    status_label = ctk.CTkLabel(control_frame, text="Ready to test async loading")
    status_label.pack(side="right", padx=10)
    
    def update_status():
        """Update status periodically to show UI is responsive."""
        count = 0
        while True:
            count += 1
            status_label.configure(text=f"UI responsive - tick {count}")
            time.sleep(1)
    
    # Start status update thread
    threading.Thread(target=update_status, daemon=True).start()
    
    print("Test window opened. Try:")
    print("1. Click 'Load Large Plan' - UI should remain responsive")
    print("2. Try scrolling and clicking while loading")
    print("3. Check that status counter keeps updating")
    print("4. Switch to other tabs to test responsiveness")
    
    root.mainloop()

if __name__ == "__main__":
    test_async_loading() 