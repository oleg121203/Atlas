import json
import os
import sys

# Add the parent directory to the path so we can import from modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.natural_language_workflow import NLWorkflowGenerator


def demonstrate_nl_workflow_generator():
    """Demonstrate the natural language to workflow generator functionality"""
    print("Initializing Natural Language to Workflow Generator...")
    generator = NLWorkflowGenerator()

    print("\nFine-tuning model with existing patterns and history...")
    success = generator.fine_tune_model()
    if success:
        print("Fine-tuning completed successfully")
    else:
        print("Fine-tuning failed")
        return

    print("\nDemonstrating workflow generation from natural language input...")
    test_cases = [
        "Create a workflow for processing customer feedback surveys and generating a summary report",
        "Design a workflow for automated email follow-ups with customers after purchase",
        "Build a data processing pipeline for cleaning and analyzing sales data",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_input}")
        workflow = generator.generate_workflow(test_input)
        if workflow:
            print("Generated Workflow Structure:")
            print(
                json.dumps(workflow, indent=2)[:1000] + "..."
                if len(json.dumps(workflow, indent=2)) > 1000
                else json.dumps(workflow, indent=2)
            )
        else:
            print("Failed to generate workflow")


if __name__ == "__main__":
    demonstrate_nl_workflow_generator()
