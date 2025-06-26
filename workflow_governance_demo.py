from workflow_governance import WorkflowGovernance, ComplianceStandard, AccessRole
import json

# Initialize the WorkflowGovernance instance
def run_demo():
    """Run a demonstration of the Workflow Governance capabilities."""
    governance = WorkflowGovernance()
    workflow_id = "demo_workflow"
    version = "1.0.0"
    user_id = "demo_user"
    approver_id = "demo_approver"
    
    # Define a sample workflow
    sample_workflow = {
        "name": "Demo Workflow",
        "description": "A sample workflow for governance demo",
        "steps": [
            {"id": 1, "action": "Collect Data"},
            {"id": 2, "action": "Process Data"},
            {"id": 3, "action": "Publish Results"}
        ],
        "personal_data": True,
        "changes": "Initial version for demo"
    }
    
    # Version the workflow
    print(f"Versioning workflow: {workflow_id} as version {version}")
    governance.version_workflow(workflow_id, sample_workflow, version)
    print("Version created successfully.")
    print("Version history:")
    print(json.dumps(governance.workflow_versions[workflow_id], indent=2))
    
    # Request approval for deployment
    print(f"\nRequesting approval for {workflow_id} version {version}")
    governance.request_approval(workflow_id, version, user_id, "Initial deployment request")
    print("Approval requested successfully.")
    print("Approval records:")
    print(json.dumps(governance.approval_records[workflow_id], indent=2))
    
    # Approve the workflow
    print(f"\nApproving {workflow_id} version {version}")
    governance.approve_workflow(workflow_id, version, approver_id, "approved", "Approved for production")
    print("Workflow approved successfully.")
    print("Updated approval records:")
    print(json.dumps(governance.approval_records[workflow_id], indent=2))
    
    # Run compliance check
    print(f"\nRunning GDPR compliance check for {workflow_id}")
    compliance_result = governance.run_compliance_check(workflow_id, ComplianceStandard.GDPR, sample_workflow)
    print("Compliance check result:")
    print(json.dumps(compliance_result, indent=2))
    
    # Configure role-based access control
    print(f"\nConfiguring access roles for {workflow_id}")
    governance.configure_role_access(workflow_id, AccessRole.ADMIN, ["view", "edit", "execute", "approve"])
    governance.configure_role_access(workflow_id, AccessRole.EDITOR, ["view", "edit"])
    governance.configure_role_access(workflow_id, AccessRole.VIEWER, ["view"])
    print("Role permissions configured.")
    
    # Assign role to user
    print(f"Assigning Admin role to {user_id} for {workflow_id}")
    governance.assign_user_role(user_id, workflow_id, AccessRole.ADMIN)
    print("Role assigned.")
    
    # Check user access
    print(f"Checking if {user_id} can edit {workflow_id}")
    can_edit = governance.check_user_access(user_id, workflow_id, "edit")
    print(f"User can edit: {can_edit}")
    print(f"Checking if {user_id} can delete {workflow_id}")
    can_delete = governance.check_user_access(user_id, workflow_id, "delete")
    print(f"User can delete: {can_delete}")
    
    # View audit trail
    print(f"\nAudit trail for {workflow_id}:")
    audit_trail = governance.get_audit_trail(workflow_id)
    print(json.dumps(audit_trail, indent=2))

if __name__ == "__main__":
    print("Starting Workflow Governance Demo")
    print("=====================================")
    run_demo()
    print("=====================================")
    print("Demo completed.")
