import unittest
from workflow.workflow_resource_management import WorkflowResourceManager, ResourceType, PriorityLevel
from typing import Dict, List, Any
from datetime import datetime

class TestWorkflowResourceManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = WorkflowResourceManager()
        self.workflow_id = "test_workflow"
        self.resource_id = "test_cpu_01"
        self.environment_id = "test_env"
        
        # Register a test resource
        self.manager.register_resource(self.resource_id, ResourceType.CPU, 8.0, "cores", "data_center_1", 0.10)

    def test_register_resource(self):
        """Test registering a resource."""
        self.assertIn(self.resource_id, self.manager.resources)
        resource = self.manager.resources[self.resource_id]
        self.assertEqual(resource["type"], ResourceType.CPU.value)
        self.assertEqual(resource["capacity"], 8.0)
        self.assertEqual(resource["unit"], "cores")
        self.assertEqual(resource["location"], "data_center_1")
        self.assertEqual(resource["cost_per_hour"], 0.10)

    def test_allocate_resource(self):
        """Test allocating a resource to a workflow."""
        result = self.manager.allocate_resource(self.workflow_id, self.resource_id, 2.0, 1.0)
        self.assertTrue(result)
        self.assertIn(self.workflow_id, self.manager.allocations)
        allocations = self.manager.allocations[self.workflow_id]
        self.assertEqual(len(allocations), 1)
        resource = self.manager.resources[self.resource_id]
        self.assertEqual(resource["available"], 6.0)

    def test_allocate_resource_insufficient_capacity(self):
        """Test allocating a resource when capacity is insufficient."""
        result = self.manager.allocate_resource(self.workflow_id, self.resource_id, 10.0, 1.0)
        self.assertFalse(result)
        self.assertNotIn(self.workflow_id, self.manager.allocations)

    def test_release_resource(self):
        """Test releasing a resource allocation."""
        self.manager.allocate_resource(self.workflow_id, self.resource_id, 2.0, 1.0)
        allocations = self.manager.allocations[self.workflow_id]
        allocation_id = list(allocations.keys())[0]
        result = self.manager.release_resource(self.workflow_id, allocation_id)
        self.assertTrue(result)
        self.assertFalse(allocations[allocation_id]["active"])
        resource = self.manager.resources[self.resource_id]
        self.assertEqual(resource["available"], 8.0)

    def test_schedule_workflow(self):
        """Test scheduling a workflow with required resources."""
        start_time = datetime.now().isoformat()
        required_resources = [
            {"type": ResourceType.CPU.value, "amount": 2.0},
            {"type": ResourceType.MEMORY.value, "amount": 4.0}
        ]
        result = self.manager.schedule_workflow(self.workflow_id, start_time, 2.0, required_resources, PriorityLevel.HIGH)
        self.assertTrue(result)
        self.assertIn(self.workflow_id, self.manager.schedules)
        schedule = self.manager.schedules[self.workflow_id]
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["status"], "scheduled")
        self.assertEqual(self.manager.priority_queue[self.workflow_id], PriorityLevel.HIGH)

    def test_update_capacity_plan(self):
        """Test updating capacity plan for an environment."""
        plan_details = {"cpu_cores": 16, "memory_gb": 32, "storage_tb": 1}
        self.manager.update_capacity_plan(self.environment_id, plan_details, 30)
        self.assertIn(self.environment_id, self.manager.capacity_plans)
        plan = self.manager.capacity_plans[self.environment_id]
        self.assertEqual(plan["details"], plan_details)
        self.assertEqual(plan["forecast_period_days"], 30)

    def test_optimize_costs(self):
        """Test cost optimization for cloud resources."""
        cloud_resources = {
            "cpu": [
                {"id": "cpu_small", "performance": 2, "cost": 0.05},
                {"id": "cpu_medium", "performance": 4, "cost": 0.10},
                {"id": "cpu_large", "performance": 8, "cost": 0.20}
            ],
            "memory": [
                {"id": "mem_small", "performance": 4, "cost": 0.03},
                {"id": "mem_large", "performance": 16, "cost": 0.12}
            ]
        }
        performance_reqs = {"cpu": 3, "memory": 8}
        result = self.manager.optimize_costs(self.workflow_id, cloud_resources, 0.25, performance_reqs)
        self.assertIn("selected_resources", result)
        self.assertIn("cpu", result["selected_resources"])
        self.assertIn("memory", result["selected_resources"])
        self.assertLessEqual(result["estimated_cost"], 0.25)
        self.assertTrue(result["meets_performance"])
        self.assertIn(self.workflow_id, self.manager.cost_optimizations)

    def test_set_resource_dependency(self):
        """Test setting resource dependencies between workflows."""
        dependent_ids = ["dependent_wf_1", "dependent_wf_2"]
        self.manager.set_resource_dependency(self.workflow_id, dependent_ids)
        self.assertIn(self.workflow_id, self.manager.dependency_map)
        self.assertEqual(self.manager.dependency_map[self.workflow_id], dependent_ids)

    def test_get_resource_usage_history(self):
        """Test retrieving resource usage history."""
        self.manager.allocate_resource(self.workflow_id, self.resource_id, 2.0, 1.0)
        history = self.manager.get_resource_usage_history(self.resource_id)
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[0]["workflow_id"], self.workflow_id)
        self.assertEqual(history[0]["amount"], 2.0)

    def test_get_available_resources(self):
        """Test retrieving available resources by type."""
        available = self.manager.get_available_resources(ResourceType.CPU)
        self.assertIn(self.resource_id, available)
        self.assertEqual(available[self.resource_id]["type"], ResourceType.CPU.value)
        available_all = self.manager.get_available_resources()
        self.assertIn(self.resource_id, available_all)

    def test_get_workflow_schedule(self):
        """Test retrieving workflow schedule."""
        start_time = datetime.now().isoformat()
        required_resources = [{"type": ResourceType.CPU.value, "amount": 2.0}]
        self.manager.schedule_workflow(self.workflow_id, start_time, 2.0, required_resources, PriorityLevel.MEDIUM)
        schedule = self.manager.get_workflow_schedule(self.workflow_id)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["start_time"], start_time)

if __name__ == '__main__':
    unittest.main()
