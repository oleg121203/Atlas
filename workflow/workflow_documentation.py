"""
Workflow Documentation System Module

This module enhances the documentation of workflows by providing structured templates,
automated extraction from code, visual diagram generation, versioning, and UI integration.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import networkx as nx
from workflow_analytics import WorkflowAnalytics


class WorkflowDocumentation:
    def __init__(self, analytics: Optional[WorkflowAnalytics] = None):
        self.analytics = analytics
        self.templates: Dict[str, str] = {}
        self.documentation: Dict[str, Dict] = {}
        self.versions: Dict[str, List[Dict]] = {}
        self.version_history: Dict[str, List[Dict]] = {}

    def register_template(self, template_id: str, template_content: str):
        """
        Register a structured documentation template for workflows.
        """
        self.templates[template_id] = template_content

    def create_documentation(
        self,
        workflow_id: str,
        template_id: str,
        content: Dict[str, str],
        version: str = "1.0.0",
    ):
        """
        Create documentation for a workflow using a registered template.
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        doc_entry = {
            "template_id": template_id,
            "content": content,
            "version": version,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        self.documentation[workflow_id] = doc_entry
        if workflow_id not in self.versions:
            self.versions[workflow_id] = []
        self.versions[workflow_id].append(
            {
                "version": version,
                "timestamp": datetime.now(),
                "changes": "Initial documentation",
            }
        )

    def update_documentation(
        self,
        workflow_id: str,
        content_updates: Dict[str, str],
        version: str,
        changes: str,
    ):
        """
        Update existing documentation with new content and version information.
        """
        if workflow_id not in self.documentation:
            raise ValueError(f"No documentation found for workflow {workflow_id}")

        doc = self.documentation[workflow_id]
        doc["content"].update(content_updates)
        doc["version"] = version
        doc["updated_at"] = datetime.now()

        self.versions[workflow_id].append(
            {"version": version, "timestamp": datetime.now(), "changes": changes}
        )

    def extract_documentation_from_code(self, code_content: str) -> Dict[str, Any]:
        """
        Extract structured documentation from code comments and docstrings.

        Args:
            code_content (str): The source code content to analyze.

        Returns:
            Dict[str, Any]: Extracted documentation with name, description, parameters, returns, and steps.
        """
        doc_content = {
            "name": "",
            "description": "",
            "parameters": [],
            "returns": "",
            "steps": [],
        }

        # Extract workflow name from comments like # Workflow: Name
        name_match = re.search(r"# Workflow: (.*?)\n", code_content)
        if name_match:
            doc_content["name"] = name_match.group(1).strip()

        # Extract description from comments like # Description: Text
        desc_match = re.search(r"# Description: (.*?)\n", code_content)
        if desc_match:
            doc_content["description"] = desc_match.group(1).strip()

        # Extract docstring if present
        docstring_match = re.search(r'"""(.*?)"""', code_content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            lines = docstring.split("\n")
            if lines:
                doc_content["description"] = lines[0].strip()
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith("Args:") or line.startswith("Parameters:"):
                        doc_content["parameters"] = self._parse_parameters(lines[1:])
                    elif line.startswith("Returns:"):
                        doc_content["returns"] = line.replace("Returns:", "").strip()

        # Extract inline comments for steps or additional details
        step_comments = re.findall(r"# Step: (.*?)\n", code_content)
        doc_content["steps"] = step_comments

        # Note: Removed reference to workflow_id since it's not passed as parameter
        # If needed, we could assign a default ID or handle differently
        temp_id = "extracted_temp"
        if temp_id in self.documentation:
            self.documentation[temp_id].update(doc_content)
        else:
            self.documentation[temp_id] = doc_content

        return doc_content

    def _parse_parameters(self, lines: List[str]) -> List[Dict[str, str]]:
        params = []
        in_params = False
        for line in lines:
            line = line.strip()
            if line.startswith("Args:") or line.startswith("Parameters:"):
                in_params = True
                continue
            elif not line or line.startswith("Returns:") or line.startswith("Raises:"):
                in_params = False
                break
            if in_params and ":" in line:
                name, desc = line.split(":", 1)
                params.append({"name": name.strip(), "description": desc.strip()})
        return params

    def generate_visual_diagram(self, workflow_id: str) -> Optional[str]:
        """
        Generate a visual diagram of the workflow using networkx.

        Args:
            workflow_id (str): Identifier for the workflow template.

        Returns:
            Optional[str]: String representation of the diagram, or None if workflow not found.
        """
        if workflow_id not in self.templates:
            raise KeyError(f"Workflow template {workflow_id} not found.")
            return None

        workflow = self.templates[workflow_id]
        if not workflow.get("steps"):
            return None

        # Create a directed graph
        G = nx.DiGraph()
        for i, step in enumerate(workflow["steps"]):
            step_label = f"Step {step['id']}: {step['action']}"
            G.add_node(i, label=step_label)
            if i > 0:
                G.add_edge(i - 1, i)

        # Generate a simple text representation (could be enhanced with graphviz or other viz tools)
        diagram = "Workflow Diagram:\n"
        for i in range(len(workflow["steps"])):
            diagram += (
                f"{G.nodes[i]['label']} -> "
                if i < len(workflow["steps"]) - 1
                else f"{G.nodes[i]['label']}\n"
            )
        return diagram

    def version_documentation(
        self, workflow_id: str, version_info: Dict[str, str]
    ) -> None:
        """
        Version the documentation for a specific workflow.

        Args:
            workflow_id (str): Identifier for the workflow.
            version_info (Dict[str, str]): Dictionary with version information (version number, date, etc.).
        """
        if workflow_id not in self.version_history:
            self.version_history[workflow_id] = []
        self.version_history[workflow_id].append(version_info)

    def generate_inline_help(self, workflow_id: str) -> Dict[str, Any]:
        """
        Generate inline help content for UI integration.

        Args:
            workflow_id (str): Identifier for the workflow template.

        Returns:
            Dict[str, Any]: Structured help content for the specified workflow.
        """
        if workflow_id not in self.templates:
            raise KeyError(f"Workflow template {workflow_id} not found.")

        workflow = self.templates[workflow_id]
        help_content = {
            "name": workflow.get("name", ""),
            "description": workflow.get("description", ""),
            "steps": [],
        }

        for step in workflow.get("steps", []):
            help_content["steps"].append(
                {
                    "id": step.get("id", 0),
                    "action": step.get("action", ""),
                    "help_text": f"Expect: {step.get('expected', '')}",
                }
            )

        return help_content

    def get_documentation_version_history(self, workflow_id: str) -> List[Dict]:
        """
        Retrieve the version history for a workflow's documentation.
        """
        return self.versions.get(workflow_id, [])

    def get_inline_help_content(
        self, workflow_id: str, section: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve documentation content formatted for inline help in UI.
        """
        if workflow_id not in self.documentation:
            return {"status": "not_found", "content": {}}

        doc = self.documentation[workflow_id]
        content = doc["content"]
        if section:
            content = {k: v for k, v in content.items() if k == section}

        return {
            "status": "success",
            "content": content,
            "version": doc["version"],
            "updated_at": doc["updated_at"],
        }


if __name__ == "__main__":
    # Demo usage
    doc_system = WorkflowDocumentation()

    # Register a sample template
    template = """
    Workflow Documentation Template
    ------------------------------
    Description: {description}
    Steps:
    {steps}
    Parameters:
    {parameters}
    Returns: {returns}
    """
    doc_system.register_template("default", template)

    # Create initial documentation
    initial_content = {
        "description": "Sample data processing workflow",
        "steps": "- Load data\n- Transform data\n- Save results",
        "parameters": "- input_path: Path to input data file\n- output_path: Path to save results",
        "returns": "Status of operation",
    }
    doc_system.create_documentation("sample_workflow", "default", initial_content)
    print("Initial documentation created")

    # Update documentation
    updates = {
        "description": "Updated data processing and analysis workflow",
        "steps": "- Load data\n- Clean data\n- Transform data\n- Analyze data\n- Save results",
    }
    doc_system.update_documentation(
        "sample_workflow", updates, "1.1.0", "Added data cleaning and analysis steps"
    )
    print("Documentation updated")

    # Extract documentation from sample code
    sample_code = '''
    def process_data(input_path, output_path):
        """
        Process input data and save results.
        Args:
            input_path (str): Path to input data file
            output_path (str): Path to save results
        Returns:
            bool: Status of operation
        """
        # Step: Load data
        data = load_data(input_path)
        # Step: Transform data
        transformed = transform_data(data)
        # Step: Save results
        save_results(transformed, output_path)
        return True
    '''
    extracted = doc_system.extract_documentation_from_code(sample_code)
    print(
        "Extracted documentation from code:",
        json.dumps(extracted, indent=2, default=str),
    )

    # Get version history
    history = doc_system.get_documentation_version_history("sample_workflow")
    print("Version history:", json.dumps(history, indent=2, default=str))

    # Get inline help content
    help_content = doc_system.get_inline_help_content(
        "sample_workflow", section="description"
    )
    print(
        "Inline help content (description only):",
        json.dumps(help_content, indent=2, default=str),
    )
