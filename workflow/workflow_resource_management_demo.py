import json
from datetime import datetime

from workflow_resource_management import (
    PriorityLevel,
    ResourceType,
    WorkflowResourceManager,
)


# Initialize the WorkflowResourceManager instance
def run_demo():
    """Run a demonstration of the Workflow Resource Management capabilities."""
    manager = WorkflowResourceManager()
    workflow_id = "demo_workflow"
    workflow_id_2 = "demo_workflow_2"

    # Register resources
    print("Registering resources:")
    manager.register_resource(
        "cpu_cluster_1", ResourceType.CPU, 16.0, "cores", "dc1", 0.15
    )
    manager.register_resource(
        "mem_bank_1", ResourceType.MEMORY, 64.0, "GB", "dc1", 0.05
    )
    manager.register_resource(
        "storage_array_1", ResourceType.STORAGE, 1000.0, "GB", "dc1", 0.02
    )
    manager.register_resource(
        "gpu_cluster_1", ResourceType.GPU, 4.0, "units", "dc1", 0.50
    )
    print("Resources registered.")
    print("Available resources:")
    print(json.dumps(manager.get_available_resources(), indent=2))

    # Allocate resources to workflow
    print(f"\nAllocating resources to {workflow_id}:")
    cpu_alloc = manager.allocate_resource(workflow_id, "cpu_cluster_1", 4.0, 2.0)
    mem_alloc = manager.allocate_resource(workflow_id, "mem_bank_1", 16.0, 2.0)
    print(f"CPU allocation successful: {cpu_alloc}")
    print(f"Memory allocation successful: {mem_alloc}")
    print("Updated available resources:")
    print(json.dumps(manager.get_available_resources(), indent=2))

    # Schedule workflows
    print(f"\nScheduling {workflow_id} and {workflow_id_2}:")
    start_time = datetime.now().isoformat()
    required_resources = [
        {"type": ResourceType.CPU.value, "amount": 4.0},
        {"type": ResourceType.MEMORY.value, "amount": 16.0},
    ]
    sched_1 = manager.schedule_workflow(
        workflow_id, start_time, 2.0, required_resources, PriorityLevel.HIGH
    )
    start_time_2 = datetime.now().isoformat()
    required_resources_2 = [
        {"type": ResourceType.CPU.value, "amount": 2.0},
        {"type": ResourceType.MEMORY.value, "amount": 8.0},
    ]
    sched_2 = manager.schedule_workflow(
        workflow_id_2, start_time_2, 1.5, required_resources_2, PriorityLevel.MEDIUM
    )
    print(f"Scheduling {workflow_id} successful: {sched_1}")
    print(f"Scheduling {workflow_id_2} successful: {sched_2}")
    print(f"Schedule for {workflow_id}:")
    print(json.dumps(manager.get_workflow_schedule(workflow_id), indent=2))

    # Update capacity plan
    print("\nUpdating capacity plan for test environment:")
    plan_details = {"cpu_cores": 32, "memory_gb": 128, "storage_tb": 5, "gpu_units": 8}
    manager.update_capacity_plan("test_env", plan_details, 30)
    print("Capacity plan updated.")
    print(json.dumps(manager.capacity_plans["test_env"], indent=2))

    # Optimize costs for cloud execution
    print(f"\nOptimizing costs for {workflow_id}:")
    cloud_resources = {
        "cpu": [
            {"id": "cpu_small", "performance": 2, "cost": 0.05},
            {"id": "cpu_medium", "performance": 4, "cost": 0.10},
            {"id": "cpu_large", "performance": 8, "cost": 0.20},
        ],
        "memory": [
            {"id": "mem_small", "performance": 4, "cost": 0.03},
            {"id": "mem_medium", "performance": 8, "cost": 0.06},
            {"id": "mem_large", "performance": 16, "cost": 0.12},
        ],
    }
    performance_reqs = {"cpu": 3, "memory": 10}
    budget = 0.30
    opt_result = manager.optimize_costs(
        workflow_id, cloud_resources, budget, performance_reqs
    )
    print("Cost optimization result:")
    print(json.dumps(opt_result, indent=2))

    # Set resource dependencies
    print(f"\nSetting resource dependencies for {workflow_id}:")
    dependents = [workflow_id_2, "demo_workflow_3"]
    manager.set_resource_dependency(workflow_id, dependents)
    print("Dependencies set.")
    print(json.dumps(manager.dependency_map[workflow_id], indent=2))

    # View resource usage history
    print("\nResource usage history for cpu_cluster_1:")
    history = manager.get_resource_usage_history("cpu_cluster_1")
    print(json.dumps(history, indent=2))

    # Release resources
    print(f"\nReleasing resources for {workflow_id}:")
    allocations = manager.allocations[workflow_id]
    for alloc_id in allocations:
        released = manager.release_resource(workflow_id, alloc_id)
        print(f"Resource {alloc_id} released: {released}")
    print("Final available resources:")
    print(json.dumps(manager.get_available_resources(), indent=2))


if __name__ == "__main__":
    print("Starting Workflow Resource Management Demo")
    print("=====================================")
    run_demo()
    print("=====================================")
    print("Demo completed.")
