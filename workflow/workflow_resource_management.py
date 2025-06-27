import json
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ResourceType(Enum):
    CPU = "CPU"
    MEMORY = "Memory"
    STORAGE = "Storage"
    NETWORK = "Network"
    GPU = "GPU"
    CLOUD_INSTANCE = "CloudInstance"


class PriorityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class WorkflowResourceManager:
    def __init__(self):
        """
        Initialize the Workflow Resource Management system.
        """
        self.resources: Dict[str, Dict] = {}
        self.allocations: Dict[str, Dict[str, Any]] = {}
        self.schedules: Dict[str, List[Dict]] = {}
        self.capacity_plans: Dict[str, Dict] = {}
        self.cost_optimizations: Dict[str, Dict] = {}
        self.priority_queue: Dict[str, PriorityLevel] = {}
        self.dependency_map: Dict[str, List[str]] = {}
        self.usage_history: Dict[str, List[Dict]] = {}

    def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        capacity: float,
        unit: str,
        location: Optional[str] = None,
        cost_per_hour: Optional[float] = None,
    ) -> None:
        """
        Register a resource available for workflow execution.

        Args:
            resource_id (str): Unique identifier for the resource.
            resource_type (ResourceType): Type of resource (CPU, Memory, etc.).
            capacity (float): Capacity of the resource.
            unit (str): Unit of measurement for capacity (e.g., 'cores', 'GB', 'Mbps').
            location (Optional[str]): Physical or logical location of the resource.
            cost_per_hour (Optional[float]): Cost per hour of using the resource.
        """
        self.resources[resource_id] = {
            "type": resource_type.value,
            "capacity": capacity,
            "unit": unit,
            "location": location or "default",
            "cost_per_hour": cost_per_hour or 0.0,
            "available": capacity,
            "last_updated": datetime.now().isoformat(),
        }
        self.usage_history[resource_id] = []

    def allocate_resource(
        self,
        workflow_id: str,
        resource_id: str,
        amount: float,
        duration_hours: float,
        start_time: Optional[str] = None,
    ) -> bool:
        """
        Allocate a resource to a workflow for a specified duration.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            resource_id (str): Unique identifier for the resource.
            amount (float): Amount of resource to allocate.
            duration_hours (float): Duration in hours for the allocation.
            start_time (Optional[str]): ISO format start time for the allocation.

        Returns:
            bool: True if allocation is successful, False otherwise.
        """
        if resource_id not in self.resources:
            return False

        resource = self.resources[resource_id]
        if resource["available"] < amount:
            return False

        start = start_time or datetime.now().isoformat()
        end = datetime.fromisoformat(start).timestamp() + (duration_hours * 3600)
        end_time = datetime.fromtimestamp(end).isoformat()

        if workflow_id not in self.allocations:
            self.allocations[workflow_id] = {}

        allocation_id = f"alloc_{workflow_id}_{resource_id}_{start}"
        self.allocations[workflow_id][allocation_id] = {
            "resource_id": resource_id,
            "amount": amount,
            "start_time": start,
            "end_time": end_time,
            "duration_hours": duration_hours,
            "active": True,
        }

        resource["available"] -= amount
        resource["last_updated"] = datetime.now().isoformat()

        self.usage_history[resource_id].append(
            {
                "workflow_id": workflow_id,
                "amount": amount,
                "start_time": start,
                "end_time": end_time,
                "allocation_id": allocation_id,
            }
        )
        return True

    def release_resource(self, workflow_id: str, allocation_id: str) -> bool:
        """
        Release a resource allocation back to the pool.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            allocation_id (str): Unique identifier for the allocation.

        Returns:
            bool: True if resource is successfully released.
        """
        if (
            workflow_id not in self.allocations
            or allocation_id not in self.allocations[workflow_id]
        ):
            return False

        allocation = self.allocations[workflow_id][allocation_id]
        if not allocation["active"]:
            return False

        resource_id = allocation["resource_id"]
        amount = allocation["amount"]
        self.resources[resource_id]["available"] += amount
        self.resources[resource_id]["last_updated"] = datetime.now().isoformat()
        allocation["active"] = False
        allocation["end_time"] = datetime.now().isoformat()
        return True

    def schedule_workflow(
        self,
        workflow_id: str,
        start_time: str,
        estimated_duration_hours: float,
        required_resources: List[Dict[str, Any]],
        priority: PriorityLevel,
    ) -> bool:
        """
        Schedule a workflow for execution with required resources.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            start_time (str): ISO format start time for the workflow.
            estimated_duration_hours (float): Estimated duration in hours.
            required_resources (List[Dict[str, Any]]): List of required resources with type and amount.
            priority (PriorityLevel): Priority level for the workflow.

        Returns:
            bool: True if scheduling is successful.
        """
        if workflow_id not in self.schedules:
            self.schedules[workflow_id] = []

        end_time = datetime.fromisoformat(start_time).timestamp() + (
            estimated_duration_hours * 3600
        )
        end_time_str = datetime.fromtimestamp(end_time).isoformat()

        schedule_entry = {
            "start_time": start_time,
            "end_time": end_time_str,
            "duration_hours": estimated_duration_hours,
            "required_resources": required_resources,
            "status": "scheduled",
            "priority": priority.value,
        }
        self.schedules[workflow_id].append(schedule_entry)
        self.priority_queue[workflow_id] = priority
        return True

    def update_capacity_plan(
        self,
        environment_id: str,
        plan_details: Dict[str, Any],
        forecast_period_days: int,
    ) -> None:
        """
        Update capacity planning for workflow execution environments.

        Args:
            environment_id (str): Unique identifier for the environment.
            plan_details (Dict[str, Any]): Capacity plan details.
            forecast_period_days (int): Forecast period in days.
        """
        self.capacity_plans[environment_id] = {
            "details": plan_details,
            "forecast_period_days": forecast_period_days,
            "last_updated": datetime.now().isoformat(),
        }

    def optimize_costs(
        self,
        workflow_id: str,
        cloud_resources: Dict[str, Any],
        budget_limit: float,
        performance_requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Optimize costs for cloud-based workflow execution.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            cloud_resources (Dict[str, Any]): Available cloud resources and pricing.
            budget_limit (float): Budget limit for execution.
            performance_requirements (Dict[str, Any]): Performance requirements (e.g., latency, throughput).

        Returns:
            Dict[str, Any]: Optimized resource selection within budget.
        """
        # Simplified cost optimization logic
        optimization_result = {
            "workflow_id": workflow_id,
            "selected_resources": {},
            "estimated_cost": 0.0,
            "meets_performance": True,
            "optimization_time": datetime.now().isoformat(),
        }

        total_cost = 0.0
        for res_type, req in performance_requirements.items():
            if res_type in cloud_resources:
                # Select cheapest resource meeting requirements
                options = cloud_resources[res_type]
                selected = None
                min_cost = float("inf")
                for option in options:
                    if (
                        option.get("performance", 0) >= req
                        and option.get("cost", float("inf")) < min_cost
                    ):
                        selected = option
                        min_cost = option.get("cost", 0.0)
                if selected:
                    optimization_result["selected_resources"][res_type] = selected
                    total_cost += min_cost

        optimization_result["estimated_cost"] = total_cost
        if total_cost > budget_limit:
            optimization_result["meets_performance"] = False

        self.cost_optimizations[workflow_id] = optimization_result
        return optimization_result

    def set_resource_dependency(
        self, workflow_id: str, dependent_workflow_ids: List[str]
    ) -> None:
        """
        Set dependencies between workflows for shared resources.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            dependent_workflow_ids (List[str]): List of workflow IDs that depend on this workflow.
        """
        self.dependency_map[workflow_id] = dependent_workflow_ids

    def get_resource_usage_history(
        self,
        resource_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get usage history for a specific resource.

        Args:
            resource_id (str): Unique identifier for the resource.
            start_time (Optional[str]): Start time filter in ISO format.
            end_time (Optional[str]): End time filter in ISO format.

        Returns:
            List[Dict]: List of usage records for the resource.
        """
        if resource_id not in self.usage_history:
            return []

        history = self.usage_history[resource_id]
        if start_time or end_time:
            filtered_history = []
            for entry in history:
                if start_time and entry["start_time"] < start_time:
                    continue
                if end_time and entry["end_time"] > end_time:
                    continue
                filtered_history.append(entry)
            return filtered_history
        return history

    def get_available_resources(
        self, resource_type: Optional[ResourceType] = None
    ) -> Dict[str, Dict]:
        """
        Get list of available resources, optionally filtered by type.

        Args:
            resource_type (Optional[ResourceType]): Type of resource to filter by.

        Returns:
            Dict[str, Dict]: Dictionary of available resources.
        """
        if resource_type:
            return {
                k: v
                for k, v in self.resources.items()
                if v["type"] == resource_type.value
            }
        return self.resources

    def get_workflow_schedule(self, workflow_id: str) -> List[Dict]:
        """
        Get scheduled executions for a workflow.

        Args:
            workflow_id (str): Unique identifier for the workflow.

        Returns:
            List[Dict]: List of scheduled executions.
        """
        return self.schedules.get(workflow_id, [])

    def save_resource_data(self, file_path: str) -> None:
        """
        Save resource management data to a file for persistence.

        Args:
            file_path (str): Path to save the data.
        """
        data = {
            "resources": self.resources,
            "allocations": self.allocations,
            "schedules": self.schedules,
            "capacity_plans": self.capacity_plans,
            "cost_optimizations": self.cost_optimizations,
            "priority_queue": {k: v.value for k, v in self.priority_queue.items()},
            "dependency_map": self.dependency_map,
            "usage_history": self.usage_history,
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_resource_data(self, file_path: str) -> None:
        """
        Load resource management data from a file.

        Args:
            file_path (str): Path to load the data from.
        """
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                self.resources = data.get("resources", {})
                self.allocations = data.get("allocations", {})
                self.schedules = data.get("schedules", {})
                self.capacity_plans = data.get("capacity_plans", {})
                self.cost_optimizations = data.get("cost_optimizations", {})
                priority_data = data.get("priority_queue", {})
                self.priority_queue = {
                    k: PriorityLevel(v) for k, v in priority_data.items()
                }
                self.dependency_map = data.get("dependency_map", {})
                self.usage_history = data.get("usage_history", {})
