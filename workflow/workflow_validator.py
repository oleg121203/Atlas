from typing import Any, Dict, List


class WorkflowValidator:
    """Class to validate workflow structures for executability"""

    def __init__(self):
        """Initialize the workflow validator"""
        self.required_fields = {"name", "steps", "metadata"}
        self.required_step_fields = {"id", "action", "parameters", "dependencies"}

    def validate_workflow(self, workflow: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a workflow dictionary for structure and executability

        Args:
            workflow (Dict[str, Any]): The workflow structure to validate

        Returns:
            tuple[bool, List[str]]: Tuple of (is_valid, list of error messages)
        """
        errors = []
        is_valid = True

        # Check for required top-level fields
        for field in self.required_fields:
            if field not in workflow:
                errors.append(f"Missing required field: {field}")
                is_valid = False

        if not is_valid:
            return is_valid, errors

        # Validate steps array
        if not isinstance(workflow["steps"], list):
            errors.append("Steps must be a list")
            is_valid = False
            return is_valid, errors

        if not workflow["steps"]:
            errors.append("Workflow must have at least one step")
            is_valid = False

        # Validate each step
        step_ids = set()
        for i, step in enumerate(workflow["steps"]):
            step_valid, step_errors = self._validate_step(step, step_ids)
            if not step_valid:
                is_valid = False
                errors.extend(
                    [
                        f"Step {i + 1} ({step.get('id', 'unknown')}): {err}"
                        for err in step_errors
                    ]
                )
            step_ids.add(step.get("id", f"step_{i}"))

        # Validate dependencies
        dependency_valid, dependency_errors = self._validate_dependencies(
            workflow["steps"], step_ids
        )
        if not dependency_valid:
            is_valid = False
            errors.extend(dependency_errors)

        return is_valid, errors

    def _validate_step(
        self, step: Dict[str, Any], existing_ids: set
    ) -> tuple[bool, List[str]]:
        """Validate an individual step in the workflow

        Args:
            step (Dict[str, Any]): The step dictionary to validate
            existing_ids (set): Set of existing step IDs for uniqueness check

        Returns:
            tuple[bool, List[str]]: Tuple of (is_valid, list of error messages)
        """
        errors = []
        is_valid = True

        # Check for required fields in step
        for field in self.required_step_fields:
            if field not in step:
                errors.append(f"Missing required field: {field}")
                is_valid = False

        if not is_valid:
            return is_valid, errors

        # Check if ID is unique
        if step["id"] in existing_ids:
            errors.append(f"Duplicate step ID: {step['id']}")
            is_valid = False

        # Check if action is non-empty string
        if not isinstance(step["action"], str) or not step["action"]:
            errors.append("Action must be a non-empty string")
            is_valid = False

        # Check if parameters is a dictionary
        if not isinstance(step["parameters"], dict):
            errors.append("Parameters must be a dictionary")
            is_valid = False

        # Check if dependencies is a list
        if not isinstance(step["dependencies"], list):
            errors.append("Dependencies must be a list")
            is_valid = False

        return is_valid, errors

    def _validate_dependencies(
        self, steps: List[Dict[str, Any]], step_ids: set
    ) -> tuple[bool, List[str]]:
        """Validate dependencies between steps

        Args:
            steps (List[Dict[str, Any]]): List of step dictionaries
            step_ids (set): Set of all step IDs for validation

        Returns:
            tuple[bool, List[str]]: Tuple of (is_valid, list of error messages)
        """
        errors = []
        is_valid = True

        # Check for circular dependencies and invalid dependency IDs
        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i}")
            for dep_id in step.get("dependencies", []):
                if dep_id not in step_ids:
                    errors.append(f"Invalid dependency ID '{dep_id}' in step {step_id}")
                    is_valid = False
                elif dep_id == step_id:
                    errors.append(f"Self-dependency detected in step {step_id}")
                    is_valid = False

        # Check for circular dependencies using a simple path traversal
        if is_valid:
            visited = set()
            path = set()
            for step in steps:
                step_id = step.get("id")
                if step_id not in visited:
                    cycle_detected = self._detect_cycle(
                        step, steps, step_id, visited, path
                    )
                    if cycle_detected:
                        errors.append(
                            f"Circular dependency detected involving step {step_id}"
                        )
                        is_valid = False
                        break

        return is_valid, errors

    def _detect_cycle(
        self,
        step: Dict[str, Any],
        steps: List[Dict[str, Any]],
        step_id: str,
        visited: set,
        path: set,
    ) -> bool:
        """Helper method to detect cycles in dependencies

        Args:
            step (Dict[str, Any]): Current step being checked
            steps (List[Dict[str, Any]]): All steps in workflow
            step_id (str): ID of current step
            visited (set): Set of all visited step IDs
            path (set): Set of step IDs in current path

        Returns:
            bool: True if cycle detected, False otherwise
        """
        visited.add(step_id)
        path.add(step_id)

        for dep_id in step.get("dependencies", []):
            if dep_id in path:
                return True
            # Find the step with this dep_id
            dep_step = next((s for s in steps if s.get("id") == dep_id), None)
            if (
                dep_step
                and dep_id not in visited
                and self._detect_cycle(dep_step, steps, dep_id, visited, path)
            ):
                return True

        path.remove(step_id)
        return False
