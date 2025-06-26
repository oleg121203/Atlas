import unittest
from workflow.workflow_governance import WorkflowGovernance, ComplianceStandard, AccessRole
from typing import Dict, Any
from datetime import datetime

class TestWorkflowGovernance(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.governance = WorkflowGovernance()
        self.workflow_id = "test_workflow"
        self.version = "1.0.0"
        self.user_id = "test_user"
        self.workflow_data = {
            "name": "Test Workflow",
            "steps": ["step1", "step2"],
            "changes": "Initial version"
        }

    def test_version_workflow(self):
        """Test versioning a workflow definition."""
        self.governance.version_workflow(self.workflow_id, self.workflow_data, self.version)
        self.assertIn(self.workflow_id, self.governance.workflow_versions)
        self.assertEqual(len(self.governance.workflow_versions[self.workflow_id]), 1)
        self.assertEqual(self.governance.workflow_versions[self.workflow_id][0]["version"], self.version)

    def test_request_approval(self):
        """Test requesting approval for workflow deployment."""
        result = self.governance.request_approval(self.workflow_id, self.version, self.user_id, "Test request")
        self.assertTrue(result)
        self.assertIn(self.workflow_id, self.governance.approval_records)
        self.assertEqual(len(self.governance.approval_records[self.workflow_id]), 1)
        self.assertEqual(self.governance.approval_records[self.workflow_id][0]["status"], "pending")

    def test_approve_workflow(self):
        """Test approving a workflow for deployment."""
        self.governance.request_approval(self.workflow_id, self.version, self.user_id)
        result = self.governance.approve_workflow(self.workflow_id, self.version, "approver", "approved", "Looks good")
        self.assertTrue(result)
        self.assertEqual(self.governance.approval_records[self.workflow_id][0]["status"], "approved")
        self.assertIn("approver", self.governance.approval_records[self.workflow_id][0])

    def test_reject_workflow(self):
        """Test rejecting a workflow for deployment."""
        self.governance.request_approval(self.workflow_id, self.version, self.user_id)
        result = self.governance.approve_workflow(self.workflow_id, self.version, "approver", "rejected", "Needs revision")
        self.assertTrue(result)
        self.assertEqual(self.governance.approval_records[self.workflow_id][0]["status"], "rejected")

    def test_audit_trail_logging(self):
        """Test audit trail logging for workflow events."""
        self.governance.version_workflow(self.workflow_id, self.workflow_data, self.version)
        self.assertIn(self.workflow_id, self.governance.audit_trail)
        self.assertGreaterEqual(len(self.governance.audit_trail[self.workflow_id]), 1)
        self.assertEqual(self.governance.audit_trail[self.workflow_id][0]["event_type"], "version_created")

    def test_compliance_check_gdpr(self):
        """Test GDPR compliance check for workflow with personal data."""
        non_compliant_data = {"personal_data": True}
        result = self.governance.run_compliance_check(self.workflow_id, ComplianceStandard.GDPR, non_compliant_data)
        self.assertFalse(result["compliant"])
        self.assertGreater(len(result["issues"]), 0)

    def test_compliance_check_hipaa(self):
        """Test HIPAA compliance check for workflow with health data."""
        non_compliant_data = {"health_data": True}
        result = self.governance.run_compliance_check(self.workflow_id, ComplianceStandard.HIPAA, non_compliant_data)
        self.assertFalse(result["compliant"])
        self.assertGreater(len(result["issues"]), 0)

    def test_role_based_access_control(self):
        """Test configuring and checking role-based access control."""
        permissions = ["edit", "execute", "view"]
        self.governance.configure_role_access(self.workflow_id, AccessRole.EDITOR, permissions)
        self.governance.assign_user_role(self.user_id, self.workflow_id, AccessRole.EDITOR)
        access_result = self.governance.check_user_access(self.user_id, self.workflow_id, "edit")
        self.assertTrue(access_result)
        access_result = self.governance.check_user_access(self.user_id, self.workflow_id, "delete")
        self.assertFalse(access_result)

    def test_get_audit_trail(self):
        """Test retrieving audit trail for a workflow."""
        self.governance.version_workflow(self.workflow_id, self.workflow_data, self.version)
        audit_trail = self.governance.get_audit_trail(self.workflow_id)
        self.assertGreaterEqual(len(audit_trail), 1)
        self.assertEqual(audit_trail[0]["event_type"], "version_created")

if __name__ == '__main__':
    unittest.main()
