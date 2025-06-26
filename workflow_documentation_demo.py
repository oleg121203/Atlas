from workflow_documentation import WorkflowDocumentation
import json

# Initialize the WorkflowDocumentation instance
def run_demo():
    """Run a demonstration of the WorkflowDocumentation capabilities."""
    doc_system = WorkflowDocumentation()
    
    # Define a sample workflow template
    sample_template = {
        "name": "Sample Workflow",
        "description": "A demonstration workflow for testing documentation features.",
        "steps": [
            {"id": 1, "action": "Initialize system", "expected": "System ready"},
            {"id": 2, "action": "Process data", "expected": "Data processed"},
            {"id": 3, "action": "Generate report", "expected": "Report available"}
        ]
    }
    template_name = "sample_workflow"
    
    # Register the template
    print(f"Registering template: {template_name}")
    doc_system.register_template(template_name, sample_template)
    print("Template registered successfully.")
    
    # Generate and display visual diagram
    print("\nGenerating visual diagram for workflow:")
    diagram = doc_system.generate_visual_diagram(template_name)
    print(diagram)
    
    # Version the documentation
    version_info = {"version": "1.0.0", "date": "2023-10-05"}
    print(f"\nVersioning documentation with info: {version_info}")
    doc_system.version_documentation(template_name, version_info)
    print("Version added to history:")
    print(json.dumps(doc_system.version_history[template_name], indent=2))
    
    # Generate inline help for UI integration
    print("\nGenerating inline help content for UI:")
    inline_help = doc_system.generate_inline_help(template_name)
    print(json.dumps(inline_help, indent=2))
    
    # Simulate extracting documentation from code comments
    code_snippet = """
    # Workflow: Demo Workflow
    # Description: This demonstrates inline documentation.
    def demo_workflow():
        # Step 1: Start process
        pass
        # Step 2: Check status
        pass
    """
    print("\nExtracting documentation from code comments:")
    extracted_doc = doc_system.extract_documentation_from_code(code_snippet)
    print(json.dumps(extracted_doc, indent=2))

if __name__ == "__main__":
    print("Starting Workflow Documentation Demo")
    print("=====================================")
    run_demo()
    print("=====================================")
    print("Demo completed.")
