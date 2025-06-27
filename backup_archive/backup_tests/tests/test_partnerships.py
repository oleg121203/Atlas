"""
Unit Tests for Partnerships and Collaborations Module

This module contains tests for the PartnershipManager class, ensuring that partnership management
functionalities work as expected.
"""

import json
import os
import unittest

import pandas as pd
from modules.marketing.partnerships import PartnershipManager


class TestPartnershipManager(unittest.TestCase):
    def setUp(self):
        self.pm = PartnershipManager()
        # Clear any existing data file for a clean test environment
        self.data_file = self.pm.data_file
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        self.pm.partners = []
        self.pm.proposals = []
        self.pm.agreements = []
        self.pm.outcomes = []
        self.pm.save_data()

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_add_potential_partner(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        self.assertEqual(len(self.pm.partners), 1)
        self.assertEqual(partner["name"], "TestCorp")
        self.assertEqual(partner["industry"], "Tech")
        self.assertEqual(partner["contact_info"], "test@corp.com")
        self.assertEqual(partner["potential_value"], "High potential")
        self.assertEqual(partner["status"], "Potential")

    def test_propose_partnership(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        proposal = self.pm.propose_partnership(
            partner["id"], "Integration", "Test integration proposal"
        )
        self.assertEqual(len(self.pm.proposals), 1)
        self.assertEqual(proposal["partner_id"], partner["id"])
        self.assertEqual(proposal["partner_name"], "TestCorp")
        self.assertEqual(proposal["type"], "Integration")
        self.assertEqual(proposal["details"], "Test integration proposal")
        self.assertEqual(proposal["status"], "Draft")
        updated_partner = next(
            (p for p in self.pm.partners if p["id"] == partner["id"]), None
        )
        self.assertEqual(updated_partner["status"], "Proposal in Progress")

    def test_finalize_proposal(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        proposal = self.pm.propose_partnership(
            partner["id"], "Integration", "Test integration proposal"
        )
        finalized_proposal = self.pm.finalize_proposal(
            proposal["id"], "Accepted", "Proposal accepted with conditions"
        )
        self.assertEqual(finalized_proposal["status"], "Accepted")
        self.assertEqual(
            finalized_proposal["comments"], "Proposal accepted with conditions"
        )
        self.assertIn("updated_at", finalized_proposal)
        updated_partner = next(
            (p for p in self.pm.partners if p["id"] == partner["id"]), None
        )
        self.assertEqual(updated_partner["status"], "Proposal Accepted")

    def test_draft_agreement(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        proposal = self.pm.propose_partnership(
            partner["id"], "Integration", "Test integration proposal"
        )
        self.pm.finalize_proposal(proposal["id"], "Accepted")
        agreement = self.pm.draft_agreement(proposal["id"], "6-month integration", 6)
        self.assertEqual(len(self.pm.agreements), 1)
        self.assertEqual(agreement["proposal_id"], proposal["id"])
        self.assertEqual(agreement["partner_id"], partner["id"])
        self.assertEqual(agreement["partner_name"], "TestCorp")
        self.assertEqual(agreement["terms"], "6-month integration")
        self.assertEqual(agreement["duration_months"], 6)
        self.assertEqual(agreement["status"], "Draft")
        updated_partner = next(
            (p for p in self.pm.partners if p["id"] == partner["id"]), None
        )
        self.assertEqual(updated_partner["status"], "Agreement in Draft")

    def test_finalize_agreement(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        proposal = self.pm.propose_partnership(
            partner["id"], "Integration", "Test integration proposal"
        )
        self.pm.finalize_proposal(proposal["id"], "Accepted")
        agreement = self.pm.draft_agreement(proposal["id"], "6-month integration", 6)
        finalized_agreement = self.pm.finalize_agreement(
            agreement["id"], "Active", "Final terms for active partnership"
        )
        self.assertEqual(finalized_agreement["status"], "Active")
        self.assertEqual(
            finalized_agreement["terms"], "Final terms for active partnership"
        )
        self.assertIn("updated_at", finalized_agreement)
        updated_partner = next(
            (p for p in self.pm.partners if p["id"] == partner["id"]), None
        )
        self.assertEqual(updated_partner["status"], "Partnership Active")

    def test_record_outcome(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        proposal = self.pm.propose_partnership(
            partner["id"], "Integration", "Test integration proposal"
        )
        self.pm.finalize_proposal(proposal["id"], "Accepted")
        agreement = self.pm.draft_agreement(proposal["id"], "6-month integration", 6)
        self.pm.finalize_agreement(agreement["id"], "Active")
        metrics = {"user_acquisition": 100, "revenue_impact": 5000}
        outcome = self.pm.record_outcome(
            agreement["id"], "Integration Complete", metrics, "Successful integration"
        )
        self.assertEqual(len(self.pm.outcomes), 1)
        self.assertEqual(outcome["agreement_id"], agreement["id"])
        self.assertEqual(outcome["partner_id"], partner["id"])
        self.assertEqual(outcome["partner_name"], "TestCorp")
        self.assertEqual(outcome["type"], "Integration Complete")
        self.assertEqual(outcome["metrics"], metrics)
        self.assertEqual(outcome["notes"], "Successful integration")

    def test_get_partnership_summary(self):
        self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        summary = self.pm.get_partnership_summary()
        self.assertEqual(summary["total_partners"], 1)
        self.assertEqual(summary["potential_partners"], 1)
        self.assertEqual(summary["proposals_draft"], 0)
        self.assertEqual(summary["agreements_active"], 0)

    def test_export_partnership_data(self):
        self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        export_file = self.pm.export_partnership_data("test_partnership_export.json")
        self.assertTrue(os.path.exists(export_file))
        with open(export_file, "r") as f:
            data = json.load(f)
            self.assertIn("partners", data)
            self.assertEqual(len(data["partners"]), 1)
            self.assertIn("summary", data)
        os.remove(export_file)

    def test_get_outcomes_dataframe(self):
        partner = self.pm.add_potential_partner(
            "TestCorp", "Tech", "test@corp.com", "High potential"
        )
        proposal = self.pm.propose_partnership(
            partner["id"], "Integration", "Test integration proposal"
        )
        self.pm.finalize_proposal(proposal["id"], "Accepted")
        agreement = self.pm.draft_agreement(proposal["id"], "6-month integration", 6)
        self.pm.finalize_agreement(agreement["id"], "Active")
        metrics = {"user_acquisition": 100, "revenue_impact": 5000}
        self.pm.record_outcome(agreement["id"], "Integration Complete", metrics)
        df = self.pm.get_outcomes_dataframe()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 1)
        self.assertIn("partner_name", df.columns)
        self.assertIn("type", df.columns)
        self.assertIn("user_acquisition", df.columns)
        self.assertIn("revenue_impact", df.columns)


if __name__ == "__main__":
    unittest.main()
