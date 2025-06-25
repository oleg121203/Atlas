#!/usr/bin/env python3
"""
Test script for improved scrolling in Hierarchical Task View
"""

import customtkinter as ctk
from ui.hierarchical_task_view import HierarchicalTaskView
import time

def create_test_tasks():
    """Create a comprehensive set of test tasks to demonstrate scrolling."""
    tasks = []
    
    # Strategic level tasks
    strategic_tasks = [
        {
            "id": "1.0",
            "title": "Strategic Planning Phase",
            "description": "High-level planning and goal setting",
            "level": "strategic",
            "status": "completed",
            "progress": 1.0,
            "children": ["1.1", "1.2", "1.3"]
        },
        {
            "id": "2.0", 
            "title": "System Analysis Phase",
            "description": "Comprehensive system analysis and requirements gathering",
            "level": "strategic",
            "status": "running",
            "progress": 0.6,
            "children": ["2.1", "2.2", "2.3", "2.4"]
        },
        {
            "id": "3.0",
            "title": "Implementation Phase",
            "description": "System implementation and deployment",
            "level": "strategic", 
            "status": "pending",
            "progress": 0.0,
            "children": ["3.1", "3.2", "3.3"]
        }
    ]
    
    # Tactical level tasks
    tactical_tasks = [
        # Children of 1.0
        {
            "id": "1.1",
            "title": "Goal Definition",
            "description": "Define primary and secondary goals",
            "level": "tactical",
            "status": "completed",
            "progress": 1.0,
            "children": ["1.1.1", "1.1.2"]
        },
        {
            "id": "1.2", 
            "title": "Resource Planning",
            "description": "Plan required resources and budget",
            "level": "tactical",
            "status": "completed",
            "progress": 1.0,
            "children": ["1.2.1", "1.2.2", "1.2.3"]
        },
        {
            "id": "1.3",
            "title": "Timeline Creation",
            "description": "Create detailed project timeline",
            "level": "tactical",
            "status": "completed", 
            "progress": 1.0,
            "children": ["1.3.1"]
        },
        
        # Children of 2.0
        {
            "id": "2.1",
            "title": "Current System Assessment",
            "description": "Analyze existing system capabilities",
            "level": "tactical",
            "status": "completed",
            "progress": 1.0,
            "children": ["2.1.1", "2.1.2", "2.1.3"]
        },
        {
            "id": "2.2",
            "title": "Requirements Gathering",
            "description": "Collect and document system requirements",
            "level": "tactical", 
            "status": "running",
            "progress": 0.8,
            "children": ["2.2.1", "2.2.2", "2.2.3", "2.2.4", "2.2.5"]
        },
        {
            "id": "2.3",
            "title": "Risk Assessment",
            "description": "Identify and analyze potential risks",
            "level": "tactical",
            "status": "paused",
            "progress": 0.4,
            "children": ["2.3.1", "2.3.2"]
        },
        {
            "id": "2.4",
            "title": "Stakeholder Analysis",
            "description": "Identify and analyze stakeholders",
            "level": "tactical",
            "status": "pending",
            "progress": 0.0,
            "children": ["2.4.1", "2.4.2", "2.4.3"]
        },
        
        # Children of 3.0
        {
            "id": "3.1",
            "title": "Development Planning",
            "description": "Plan development approach and methodology",
            "level": "tactical",
            "status": "pending",
            "progress": 0.0,
            "children": ["3.1.1", "3.1.2"]
        },
        {
            "id": "3.2",
            "title": "Testing Strategy",
            "description": "Define testing approach and procedures",
            "level": "tactical",
            "status": "pending",
            "progress": 0.0,
            "children": ["3.2.1", "3.2.2", "3.2.3"]
        },
        {
            "id": "3.3",
            "title": "Deployment Planning",
            "description": "Plan system deployment and rollout",
            "level": "tactical",
            "status": "pending",
            "progress": 0.0,
            "children": ["3.3.1", "3.3.2"]
        }
    ]
    
    # Operational level tasks (many more to test scrolling)
    operational_tasks = [
        # Children of 1.1
        {"id": "1.1.1", "title": "Primary Goal Analysis", "description": "Analyze primary objectives", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        {"id": "1.1.2", "title": "Secondary Goal Analysis", "description": "Analyze secondary objectives", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        
        # Children of 1.2
        {"id": "1.2.1", "title": "Human Resource Planning", "description": "Plan required personnel", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        {"id": "1.2.2", "title": "Financial Resource Planning", "description": "Plan budget allocation", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        {"id": "1.2.3", "title": "Technical Resource Planning", "description": "Plan technical infrastructure", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        
        # Children of 1.3
        {"id": "1.3.1", "title": "Milestone Definition", "description": "Define project milestones", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        
        # Children of 2.1
        {"id": "2.1.1", "title": "Performance Analysis", "description": "Analyze current performance metrics", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        {"id": "2.1.2", "title": "Capacity Analysis", "description": "Analyze system capacity", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        {"id": "2.1.3", "title": "Bottleneck Identification", "description": "Identify system bottlenecks", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        
        # Children of 2.2 (many to test scrolling)
        {"id": "2.2.1", "title": "Functional Requirements", "description": "Gather functional requirements", "level": "operational", "status": "completed", "progress": 1.0, "children": []},
        {"id": "2.2.2", "title": "Non-Functional Requirements", "description": "Gather non-functional requirements", "level": "operational", "status": "running", "progress": 0.7, "children": []},
        {"id": "2.2.3", "title": "User Requirements", "description": "Gather user requirements", "level": "operational", "status": "running", "progress": 0.5, "children": []},
        {"id": "2.2.4", "title": "System Requirements", "description": "Gather system requirements", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "2.2.5", "title": "Integration Requirements", "description": "Gather integration requirements", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        
        # Children of 2.3
        {"id": "2.3.1", "title": "Technical Risk Assessment", "description": "Assess technical risks", "level": "operational", "status": "paused", "progress": 0.6, "children": []},
        {"id": "2.3.2", "title": "Business Risk Assessment", "description": "Assess business risks", "level": "operational", "status": "paused", "progress": 0.2, "children": []},
        
        # Children of 2.4
        {"id": "2.4.1", "title": "Internal Stakeholder Analysis", "description": "Analyze internal stakeholders", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "2.4.2", "title": "External Stakeholder Analysis", "description": "Analyze external stakeholders", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "2.4.3", "title": "Stakeholder Communication Plan", "description": "Plan stakeholder communication", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        
        # Children of 3.1
        {"id": "3.1.1", "title": "Development Methodology Selection", "description": "Select development methodology", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "3.1.2", "title": "Development Tools Selection", "description": "Select development tools", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        
        # Children of 3.2
        {"id": "3.2.1", "title": "Unit Testing Strategy", "description": "Define unit testing approach", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "3.2.2", "title": "Integration Testing Strategy", "description": "Define integration testing approach", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "3.2.3", "title": "User Acceptance Testing Strategy", "description": "Define UAT approach", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        
        # Children of 3.3
        {"id": "3.3.1", "title": "Production Deployment Plan", "description": "Plan production deployment", "level": "operational", "status": "pending", "progress": 0.0, "children": []},
        {"id": "3.3.2", "title": "Rollback Strategy", "description": "Define rollback procedures", "level": "operational", "status": "pending", "progress": 0.0, "children": []}
    ]
    
    # Combine all tasks
    tasks = strategic_tasks + tactical_tasks + operational_tasks
    
    # Add timestamps
    for task in tasks:
        task["created_at"] = time.time()
        if task["status"] in ["running", "completed"]:
            task["started_at"] = time.time() - 3600  # 1 hour ago
        if task["status"] == "completed":
            task["completed_at"] = time.time() - 1800  # 30 minutes ago
    
    return tasks

def test_hierarchical_task_view():
    """Test the improved hierarchical task view with scrolling."""
    print("Testing improved hierarchical task view with scrolling...")
    
    root = ctk.CTk()
    root.title("Hierarchical Task View - Scrolling Test")
    root.geometry("1000x700")
    
    # Create task view
    task_view = HierarchicalTaskView(root)
    task_view.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create test data
    tasks = create_test_tasks()
    
    # Create plan data
    plan_data = {
        "goal": "Test hierarchical task structure with improved scrolling",
        "root_task_id": "1.0",
        "total_tasks": len(tasks),
        "tasks": tasks
    }
    
    # Update the view with test data
    task_view.update_plan(plan_data)
    
    # Add some instructions
    instructions = ctk.CTkLabel(root, text="""
    Scrolling Test Instructions:
    
    1. Scroll through the task tree to see all tasks
    2. Click the "↓ Bottom" button to scroll to the bottom
    3. Click on different tasks to see details
    4. Test the scroll wheel and scrollbar
    5. Verify that all tasks are visible and accessible
    
    Total tasks: {} (Strategic: 3, Tactical: 10, Operational: 25)
    """.format(len(tasks)), justify="left")
    instructions.pack(pady=10)
    
    print(f"Created {len(tasks)} test tasks. Test the scrolling functionality.")
    print("You should be able to see all tasks including 2.2.1 through 3.3.2")
    
    root.mainloop()

def test_scrolling_behavior():
    """Test specific scrolling behaviors."""
    print("Testing specific scrolling behaviors...")
    
    root = ctk.CTk()
    root.title("Scrolling Behavior Test")
    root.geometry("800x600")
    
    # Create a frame with many items to test scrolling
    scroll_frame = ctk.CTkScrollableFrame(root, label_text="Test Items", height=400)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add many test items
    for i in range(50):
        item_frame = ctk.CTkFrame(scroll_frame, height=30)
        item_frame.pack(fill="x", padx=5, pady=1)
        
        label = ctk.CTkLabel(item_frame, text=f"Test Item {i+1}")
        label.pack(side="left", padx=10, pady=5)
        
        # Add some items with different levels
        if i < 5:
            level_label = ctk.CTkLabel(item_frame, text="🎯", font=ctk.CTkFont(size=14))
            level_label.pack(side="right", padx=10, pady=5)
        elif i < 15:
            level_label = ctk.CTkLabel(item_frame, text="📋", font=ctk.CTkFont(size=14))
            level_label.pack(side="right", padx=10, pady=5)
        else:
            level_label = ctk.CTkLabel(item_frame, text="⚡", font=ctk.CTkFont(size=14))
            level_label.pack(side="right", padx=10, pady=5)
    
    # Add scroll to bottom button
    scroll_btn = ctk.CTkButton(root, text="Scroll to Bottom", 
                              command=lambda: scroll_frame._parent_canvas.yview_moveto(1.0))
    scroll_btn.pack(pady=10)
    
    print("Testing basic scrolling with 50 items. Try scrolling and using the button.")
    
    root.mainloop()

def main():
    """Run scrolling tests."""
    print("Hierarchical Task View Scrolling Test Suite")
    print("=" * 50)
    
    while True:
        print("\nChoose a test:")
        print("1. Hierarchical Task View Test (with many tasks)")
        print("2. Basic Scrolling Test (50 items)")
        print("3. Run Both Tests")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_hierarchical_task_view()
        elif choice == "2":
            test_scrolling_behavior()
        elif choice == "3":
            print("Running both tests...")
            test_hierarchical_task_view()
            test_scrolling_behavior()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 