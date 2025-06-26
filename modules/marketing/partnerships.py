"""
Partnerships and Collaborations Module for Atlas

This module provides functionality for identifying potential partners, proposing co-marketing
initiatives or integrations, and tracking partnership outcomes.
"""

import json
import os
from datetime import datetime
import pandas as pd

class PartnershipManager:
    def __init__(self):
        self.partners = []
        self.proposals = []
        self.agreements = []
        self.outcomes = []
        self.data_file = "partnership_data.json"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.partners = data.get('partners', [])
                self.proposals = data.get('proposals', [])
                self.agreements = data.get('agreements', [])
                self.outcomes = data.get('outcomes', [])

    def save_data(self):
        data = {
            'partners': self.partners,
            'proposals': self.proposals,
            'agreements': self.agreements,
            'outcomes': self.outcomes
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_potential_partner(self, name, industry, contact_info, potential_value):
        partner = {
            'id': len(self.partners) + 1,
            'name': name,
            'industry': industry,
            'contact_info': contact_info,
            'potential_value': potential_value,
            'status': 'Potential',
            'added_at': datetime.now().isoformat()
        }
        self.partners.append(partner)
        self.save_data()
        return partner

    def propose_partnership(self, partner_id, proposal_type, proposal_details):
        partner = next((p for p in self.partners if p['id'] == partner_id), None)
        if not partner:
            raise ValueError(f"Partner with ID {partner_id} not found")
        proposal = {
            'id': len(self.proposals) + 1,
            'partner_id': partner_id,
            'partner_name': partner['name'],
            'type': proposal_type,
            'details': proposal_details,
            'status': 'Draft',
            'created_at': datetime.now().isoformat()
        }
        self.proposals.append(proposal)
        partner['status'] = 'Proposal in Progress'
        self.save_data()
        return proposal

    def finalize_proposal(self, proposal_id, status, comments=None):
        proposal = next((p for p in self.proposals if p['id'] == proposal_id), None)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found")
        proposal['status'] = status
        if comments:
            proposal['comments'] = comments
        proposal['updated_at'] = datetime.now().isoformat()
        partner = next((p for p in self.partners if p['id'] == proposal['partner_id']), None)
        if partner:
            partner['status'] = 'Proposal ' + status
        self.save_data()
        return proposal

    def draft_agreement(self, proposal_id, terms, duration_months, start_date=None):
        proposal = next((p for p in self.proposals if p['id'] == proposal_id), None)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found")
        if proposal['status'] != 'Accepted':
            raise ValueError(f"Proposal must be accepted before drafting an agreement")
        agreement = {
            'id': len(self.agreements) + 1,
            'proposal_id': proposal_id,
            'partner_id': proposal['partner_id'],
            'partner_name': proposal['partner_name'],
            'terms': terms,
            'duration_months': duration_months,
            'start_date': start_date if start_date else datetime.now().isoformat(),
            'status': 'Draft',
            'created_at': datetime.now().isoformat()
        }
        self.agreements.append(agreement)
        partner = next((p for p in self.partners if p['id'] == proposal['partner_id']), None)
        if partner:
            partner['status'] = 'Agreement in Draft'
        self.save_data()
        return agreement

    def finalize_agreement(self, agreement_id, status, final_terms=None):
        agreement = next((a for a in self.agreements if a['id'] == agreement_id), None)
        if not agreement:
            raise ValueError(f"Agreement with ID {agreement_id} not found")
        agreement['status'] = status
        if final_terms:
            agreement['terms'] = final_terms
        agreement['updated_at'] = datetime.now().isoformat()
        partner = next((p for p in self.partners if p['id'] == agreement['partner_id']), None)
        if partner:
            partner['status'] = 'Partnership ' + status
        self.save_data()
        return agreement

    def record_outcome(self, agreement_id, outcome_type, metrics, notes=None):
        agreement = next((a for a in self.agreements if a['id'] == agreement_id), None)
        if not agreement:
            raise ValueError(f"Agreement with ID {agreement_id} not found")
        outcome = {
            'id': len(self.outcomes) + 1,
            'agreement_id': agreement_id,
            'partner_id': agreement['partner_id'],
            'partner_name': agreement['partner_name'],
            'type': outcome_type,
            'metrics': metrics,
            'notes': notes if notes else "",
            'recorded_at': datetime.now().isoformat()
        }
        self.outcomes.append(outcome)
        self.save_data()
        return outcome

    def get_partners_by_status(self, status=None):
        if status:
            return [p for p in self.partners if p['status'] == status]
        return self.partners

    def get_proposals_by_status(self, status=None):
        if status:
            return [p for p in self.proposals if p['status'] == status]
        return self.proposals

    def get_agreements_by_status(self, status=None):
        if status:
            return [a for a in self.agreements if a['status'] == status]
        return self.agreements

    def get_partnership_outcomes(self, partner_id=None):
        if partner_id:
            return [o for o in self.outcomes if o['partner_id'] == partner_id]
        return self.outcomes

    def get_partnership_summary(self):
        summary = {
            'total_partners': len(self.partners),
            'potential_partners': len([p for p in self.partners if p['status'] == 'Potential']),
            'proposals_draft': len([p for p in self.proposals if p['status'] == 'Draft']),
            'proposals_sent': len([p for p in self.proposals if p['status'] == 'Sent']),
            'proposals_accepted': len([p for p in self.proposals if p['status'] == 'Accepted']),
            'proposals_rejected': len([p for p in self.proposals if p['status'] == 'Rejected']),
            'agreements_draft': len([a for a in self.agreements if a['status'] == 'Draft']),
            'agreements_active': len([a for a in self.agreements if a['status'] == 'Active']),
            'agreements_completed': len([a for a in self.agreements if a['status'] == 'Completed']),
            'total_outcomes_recorded': len(self.outcomes)
        }
        return summary

    def export_partnership_data(self, filename):
        all_data = {
            'partners': self.partners,
            'proposals': self.proposals,
            'agreements': self.agreements,
            'outcomes': self.outcomes,
            'summary': self.get_partnership_summary()
        }
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        return filename

    def get_outcomes_dataframe(self):
        if not self.outcomes:
            return pd.DataFrame()
        # Flatten the metrics for DataFrame
        flattened_outcomes = []
        for outcome in self.outcomes:
            record = {
                'partner_name': outcome['partner_name'],
                'type': outcome['type'],
                'recorded_at': outcome['recorded_at']
            }
            record.update(outcome['metrics'])
            flattened_outcomes.append(record)
        return pd.DataFrame(flattened_outcomes)

# Example usage
if __name__ == "__main__":
    pm = PartnershipManager()
    # Add potential partners
    pm.add_potential_partner("TechCorp", "Productivity Software", "contact@techcorp.com", "High - potential integration")
    pm.add_potential_partner("ProductivityPlus", "Tech Consulting", "info@productivityplus.com", "Medium - co-marketing opportunity")
    # Propose partnerships
    pm.propose_partnership(1, "Integration", "Integrate Atlas with TechCorp's task management API")
    pm.propose_partnership(2, "Co-Marketing", "Joint webinar series with ProductivityPlus")
    # Finalize proposals
    pm.finalize_proposal(1, "Accepted", "TechCorp is interested in API integration")
    pm.finalize_proposal(2, "Sent", "Proposal sent, awaiting response")
    # Draft agreement for accepted proposal
    pm.draft_agreement(1, "6-month pilot integration project with API access and co-branded marketing", 6)
    # Finalize agreement
    pm.finalize_agreement(1, "Active")
    # Record outcomes
    pm.record_outcome(1, "Integration Milestone", {"milestone": "API Integration Complete", "user_acquisition": 500, "revenue_impact": 10000}, "Successful initial integration")
    pm.record_outcome(1, "User Feedback", {"positive_feedback": 85, "issues_reported": 12}, "Users appreciate the new integration")
    # Get summary
    print(pm.get_partnership_summary())
    # Export data
    pm.export_partnership_data("partnership_export.json")
    # Get outcomes as DataFrame for analysis
    outcomes_df = pm.get_outcomes_dataframe()
    print(outcomes_df)
