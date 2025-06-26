from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from enum import Enum

class ComplianceStandard(Enum):
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    ISO27001 = "ISO27001"
    SOC2 = "SOC2"

class AccessRole(Enum):
    ADMIN = "Administrator"
    EDITOR = "Editor"
    VIEWER = "Viewer"
    EXECUTOR = "Executor"

class WorkflowGovernance:
    def __init__(self):
        """
        Initialize the Workflow Governance and Compliance system.
        """
        self.workflow_versions: Dict[str, List[Dict]] = {}
        self.approval_records: Dict[str, List[Dict]] = {}
        self.audit_trail: Dict[str, List[Dict]] = {}
        self.compliance_checks: Dict[str, Dict] = {}
        self.role_access: Dict[str, Dict[str, List[str]]] = {}
        self.user_roles: Dict[str, List[str]] = {}

    def version_workflow(self, workflow_id: str, version_data: Dict[str, Any], version: str) -> None:
        """
        Version control for workflow definitions.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            version_data (Dict[str, Any]): The workflow definition data for this version.
            version (str): Version identifier.
        """
        if workflow_id not in self.workflow_versions:
            self.workflow_versions[workflow_id] = []
        
        version_info = {
            "version": version,
            "data": version_data,
            "timestamp": datetime.now().isoformat(),
            "changes": version_data.get("changes", "")
        }
        self.workflow_versions[workflow_id].append(version_info)
        self._log_audit_event(workflow_id, "version_created", {"version": version})

    def request_approval(self, workflow_id: str, version: str, requester: str, notes: Optional[str] = None) -> bool:
        """
        Request approval for a workflow version to be deployed to production.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            version (str): Version of the workflow requesting approval.
            requester (str): User requesting approval.
            notes (Optional[str]): Additional notes for the approval request.

        Returns:
            bool: True if request is logged successfully.
        """
        if workflow_id not in self.approval_records:
            self.approval_records[workflow_id] = []
        
        approval_request = {
            "version": version,
            "requester": requester,
            "status": "pending",
            "notes": notes or "",
            "timestamp": datetime.now().isoformat()
        }
        self.approval_records[workflow_id].append(approval_request)
        self._log_audit_event(workflow_id, "approval_requested", {"version": version, "requester": requester})
        return True

    def approve_workflow(self, workflow_id: str, version: str, approver: str, decision: str, comments: Optional[str] = None) -> bool:
        """
        Record an approval or rejection for a workflow deployment.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            version (str): Version of the workflow being approved/rejected.
            approver (str): User making the approval decision.
            decision (str): 'approved' or 'rejected'.
            comments (Optional[str]): Additional comments on the decision.

        Returns:
            bool: True if approval status updated successfully.
        """
        if workflow_id in self.approval_records:
            for record in self.approval_records[workflow_id]:
                if record["version"] == version and record["status"] == "pending":
                    record["status"] = decision
                    record["approver"] = approver
                    record["comments"] = comments or ""
                    record["decision_timestamp"] = datetime.now().isoformat()
                    self._log_audit_event(workflow_id, f"approval_{decision}", 
                                        {"version": version, "approver": approver})
                    return True
        return False

    def _log_audit_event(self, workflow_id: str, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log an event to the audit trail for tracking changes and executions.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            event_type (str): Type of event being logged.
            details (Dict[str, Any]): Details of the event.
        """
        if workflow_id not in self.audit_trail:
            self.audit_trail[workflow_id] = []
        
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.audit_trail[workflow_id].append(event)

    def run_compliance_check(self, workflow_id: str, standard: ComplianceStandard, 
                           workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run compliance checks against specified industry standards.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            standard (ComplianceStandard): Compliance standard to check against.
            workflow_data (Dict[str, Any]): Workflow definition to check for compliance.

        Returns:
            Dict[str, Any]: Results of compliance check with pass/fail status and issues.
        """
        # Placeholder for actual compliance checking logic
        check_result = {
            "standard": standard.value,
            "timestamp": datetime.now().isoformat(),
            "compliant": True,
            "issues": [],
            "checked_by": "system"
        }
        
        # Sample checks based on standard
        if standard == ComplianceStandard.GDPR:
            if "personal_data" in str(workflow_data).lower():
                if not workflow_data.get("data_protection", {}).get("encryption"):
                    check_result["compliant"] = False
                    check_result["issues"].append("Personal data processing without encryption specified.")
        elif standard == ComplianceStandard.HIPAA:
            if "health_data" in str(workflow_data).lower():
                if not workflow_data.get("data_protection", {}).get("access_logs"):
                    check_result["compliant"] = False
                    check_result["issues"].append("Health data processing without access logging specified.")
        
        if workflow_id not in self.compliance_checks:
            self.compliance_checks[workflow_id] = {}
        self.compliance_checks[workflow_id][standard.value] = check_result
        self._log_audit_event(workflow_id, "compliance_check", 
                            {"standard": standard.value, "compliant": check_result["compliant"]})
        return check_result

    def configure_role_access(self, workflow_id: str, role: AccessRole, 
                            permissions: List[str]) -> None:
        """
        Configure role-based access control for workflow management.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            role (AccessRole): Role to configure permissions for.
            permissions (List[str]): List of permission strings (e.g., 'edit', 'execute', 'view').
        """
        if workflow_id not in self.role_access:
            self.role_access[workflow_id] = {}
        self.role_access[workflow_id][role.value] = permissions
        self._log_audit_event(workflow_id, "role_access_configured", 
                            {"role": role.value, "permissions": permissions})

    def assign_user_role(self, user_id: str, workflow_id: str, role: AccessRole) -> None:
        """
        Assign a role to a user for a specific workflow.

        Args:
            user_id (str): Unique identifier for the user.
            workflow_id (str): Unique identifier for the workflow.
            role (AccessRole): Role to assign to the user.
        """
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        if role.value not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role.value)
        self._log_audit_event(workflow_id, "user_role_assigned", 
                            {"user_id": user_id, "role": role.value})

    def check_user_access(self, user_id: str, workflow_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission for a workflow based on their role.

        Args:
            user_id (str): Unique identifier for the user.
            workflow_id (str): Unique identifier for the workflow.
            permission (str): Permission to check (e.g., 'edit', 'execute', 'view').

        Returns:
            bool: True if user has the required permission, False otherwise.
        """
        if user_id not in self.user_roles:
            return False
        
        user_roles = self.user_roles[user_id]
        if workflow_id not in self.role_access:
            return False
        
        for role in user_roles:
            if role in self.role_access[workflow_id]:
                if permission in self.role_access[workflow_id][role]:
                    return True
        return False

    def get_audit_trail(self, workflow_id: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict]:
        """
        Retrieve the audit trail for a workflow, optionally filtered by date range.

        Args:
            workflow_id (str): Unique identifier for the workflow.
            start_date (Optional[str]): Start date for filtering events (ISO format).
            end_date (Optional[str]): End date for filtering events (ISO format).

        Returns:
            List[Dict]: List of audit events for the specified workflow.
        """
        if workflow_id not in self.audit_trail:
            return []
        
        events = self.audit_trail[workflow_id]
        if start_date or end_date:
            filtered_events = []
            for event in events:
                event_time = event["timestamp"]
                if start_date and event_time < start_date:
                    continue
                if end_date and event_time > end_date:
                    continue
                filtered_events.append(event)
            return filtered_events
        return events

    def save_governance_data(self, file_path: str) -> None:
        """
        Save governance data to a file for persistence.

        Args:
            file_path (str): Path to save the governance data.
        """
        data = {
            "workflow_versions": self.workflow_versions,
            "approval_records": self.approval_records,
            "audit_trail": self.audit_trail,
            "compliance_checks": self.compliance_checks,
            "role_access": self.role_access,
            "user_roles": self.user_roles
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
    def load_governance_data(self, file_path: str) -> None:
        """
        Load governance data from a file.

        Args:
            file_path (str): Path to load the governance data from.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.workflow_versions = data.get("workflow_versions", {})
                self.approval_records = data.get("approval_records", {})
                self.audit_trail = data.get("audit_trail", {})
                self.compliance_checks = data.get("compliance_checks", {})
                self.role_access = data.get("role_access", {})
                self.user_roles = data.get("user_roles", {})
