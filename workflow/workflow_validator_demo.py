import os
import sys

# Add the parent directory to the path so we can import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.workflow_validator import WorkflowValidator


def demonstrate_workflow_validator():
    """Demonstrate the workflow validator functionality"""
    print("Initializing Workflow Validator...")
    validator = WorkflowValidator()

    print("\nDemonstrating validation of different workflow structures...")
    test_cases = [
        {
            "description": "Valid workflow structure",
            "workflow": {
                "name": "Valid Workflow",
                "steps": [
                    {
                        "id": "step1",
                        "action": "initialize",
                        "parameters": {"input": "data"},
                        "dependencies": [],
                    },
                    {
                        "id": "step2",
                        "action": "process",
                        "parameters": {"method": "analyze"},
                        "dependencies": ["step1"],
                    },
                ],
                "metadata": {"version": "1.0"},
            },
        },
        {"description": "Missing required fields", "workflow": {"steps": []}},
        {
            "description": "Circular dependency",
            "workflow": {
                "name": "Circular Workflow",
                "steps": [
                    {
                        "id": "step1",
                        "action": "initialize",
                        "parameters": {},
                        "dependencies": ["step2"],
                    },
                    {
                        "id": "step2",
                        "action": "process",
                        "parameters": {},
                        "dependencies": ["step1"],
                    },
                ],
                "metadata": {},
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        is_valid, errors = validator.validate_workflow(test_case["workflow"])
        if is_valid:
            print("Validation Result: VALID")
        else:
            print("Validation Result: INVALID")
            print("Errors:")
            for error in errors:
                print(f"- {error}")


if __name__ == "__main__":
    demonstrate_workflow_validator()
