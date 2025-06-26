"""
Marketing Dashboard Module for Atlas

This module integrates social media campaigns, partnerships, and analytics into a unified dashboard
for monitoring and managing marketing efforts.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QDateEdit, QLineEdit, QMessageBox
from PySide6.QtCore import QDate
from datetime import datetime
import pandas as pd
import os
import json
from modules.marketing.social_media_campaign import SocialMediaCampaign
from modules.marketing.partnerships import PartnershipManager
from modules.marketing.analytics_feedback import MarketingAnalytics

class MarketingDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Marketing Dashboard")
        self.resize(900, 600)
        self.setup_ui()
        self.campaign_manager = SocialMediaCampaign("AtlasMarketing")
        self.partnership_manager = PartnershipManager()
        self.analytics_manager = MarketingAnalytics()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Marketing Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Tabs for different marketing areas
        tabs = QTabWidget()
        tabs.addTab(self.setup_campaigns_tab(), "Social Media Campaigns")
        tabs.addTab(self.setup_partnerships_tab(), "Partnerships")
        tabs.addTab(self.setup_analytics_tab(), "Analytics")
        layout.addWidget(tabs)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)

    def setup_campaigns_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Campaigns table
        self.campaigns_table = QTableWidget()
        self.campaigns_table.setColumnCount(5)
        self.campaigns_table.setHorizontalHeaderLabels(["ID", "Content", "Platforms", "Status", "Actions"])
        layout.addWidget(self.campaigns_table)
        
        # Add new content form
        form_layout = QHBoxLayout()
        self.content_input = QLineEdit()
        self.content_input.setPlaceholderText("Enter content idea")
        self.platforms_input = QLineEdit()
        self.platforms_input.setPlaceholderText("Platforms (comma-separated)")
        self.visual_input = QLineEdit()
        self.visual_input.setPlaceholderText("Visual description")
        add_content_btn = QPushButton("Add Content")
        add_content_btn.clicked.connect(self.add_content)
        form_layout.addWidget(self.content_input)
        form_layout.addWidget(self.platforms_input)
        form_layout.addWidget(self.visual_input)
        form_layout.addWidget(add_content_btn)
        layout.addLayout(form_layout)
        
        # Schedule post form
        schedule_layout = QHBoxLayout()
        self.schedule_id_input = QLineEdit()
        self.schedule_id_input.setPlaceholderText("Content ID to schedule")
        self.schedule_date_input = QDateEdit()
        self.schedule_date_input.setDate(QDate.currentDate())
        schedule_btn = QPushButton("Schedule Post")
        schedule_btn.clicked.connect(self.schedule_post)
        schedule_layout.addWidget(self.schedule_id_input)
        schedule_layout.addWidget(self.schedule_date_input)
        schedule_layout.addWidget(schedule_btn)
        layout.addLayout(schedule_layout)
        
        tab.setLayout(layout)
        return tab

    def setup_partnerships_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Partnerships table
        self.partnerships_table = QTableWidget()
        self.partnerships_table.setColumnCount(5)
        self.partnerships_table.setHorizontalHeaderLabels(["ID", "Name", "Industry", "Status", "Actions"])
        layout.addWidget(self.partnerships_table)
        
        # Add partner form
        partner_layout = QHBoxLayout()
        self.partner_name_input = QLineEdit()
        self.partner_name_input.setPlaceholderText("Partner name")
        self.partner_industry_input = QLineEdit()
        self.partner_industry_input.setPlaceholderText("Industry")
        self.partner_contact_input = QLineEdit()
        self.partner_contact_input.setPlaceholderText("Contact info")
        self.partner_value_input = QLineEdit()
        self.partner_value_input.setPlaceholderText("Potential value")
        add_partner_btn = QPushButton("Add Partner")
        add_partner_btn.clicked.connect(self.add_partner)
        partner_layout.addWidget(self.partner_name_input)
        partner_layout.addWidget(self.partner_industry_input)
        partner_layout.addWidget(self.partner_contact_input)
        partner_layout.addWidget(self.partner_value_input)
        partner_layout.addWidget(add_partner_btn)
        layout.addLayout(partner_layout)
        
        # Propose partnership form
        proposal_layout = QHBoxLayout()
        self.proposal_id_input = QLineEdit()
        self.proposal_id_input.setPlaceholderText("Partner ID")
        self.proposal_type_input = QLineEdit()
        self.proposal_type_input.setPlaceholderText("Proposal type")
        self.proposal_details_input = QLineEdit()
        self.proposal_details_input.setPlaceholderText("Proposal details")
        propose_btn = QPushButton("Propose Partnership")
        propose_btn.clicked.connect(self.propose_partnership)
        proposal_layout.addWidget(self.proposal_id_input)
        proposal_layout.addWidget(self.proposal_type_input)
        proposal_layout.addWidget(self.proposal_details_input)
        proposal_layout.addWidget(propose_btn)
        layout.addLayout(proposal_layout)
        
        tab.setLayout(layout)
        return tab

    def setup_analytics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Analytics summary
        self.analytics_summary = QLabel("Analytics data will be displayed here.")
        layout.addWidget(self.analytics_summary)
        
        # Channel performance table
        self.channel_table = QTableWidget()
        self.channel_table.setColumnCount(6)
        self.channel_table.setHorizontalHeaderLabels(["Channel", "Impressions", "Clicks", "Conversions", "CTR", "CPC"])
        layout.addWidget(self.channel_table)
        
        # Recommendations
        self.recommendations_label = QLabel("Recommendations will be shown here.")
        layout.addWidget(self.recommendations_label)
        
        # Record metrics form
        metrics_layout = QHBoxLayout()
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Channel")
        self.impressions_input = QLineEdit()
        self.impressions_input.setPlaceholderText("Impressions")
        self.clicks_input = QLineEdit()
        self.clicks_input.setPlaceholderText("Clicks")
        self.conversions_input = QLineEdit()
        self.conversions_input.setPlaceholderText("Conversions")
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Cost")
        record_btn = QPushButton("Record Metrics")
        record_btn.clicked.connect(self.record_metrics)
        metrics_layout.addWidget(self.channel_input)
        metrics_layout.addWidget(self.impressions_input)
        metrics_layout.addWidget(self.clicks_input)
        metrics_layout.addWidget(self.conversions_input)
        metrics_layout.addWidget(self.cost_input)
        metrics_layout.addWidget(record_btn)
        layout.addLayout(metrics_layout)
        
        visualize_btn = QPushButton("Visualize Channel Performance")
        visualize_btn.clicked.connect(self.visualize_performance)
        layout.addWidget(visualize_btn)
        
        tab.setLayout(layout)
        return tab

    def load_data(self):
        self.load_campaigns()
        self.load_partnerships()
        self.load_analytics()

    def load_campaigns(self):
        self.campaigns_table.setRowCount(0)
        for content in self.campaign_manager.get_content_plan():
            row = self.campaigns_table.rowCount()
            self.campaigns_table.insertRow(row)
            self.campaigns_table.setItem(row, 0, QTableWidgetItem(str(row)))
            self.campaigns_table.setItem(row, 1, QTableWidgetItem(content['idea']))
            self.campaigns_table.setItem(row, 2, QTableWidgetItem(", ".join(content['platforms'])))
            self.campaigns_table.setItem(row, 3, QTableWidgetItem(content['status']))
            if content['status'] == 'Draft':
                btn = QPushButton("Schedule")
                btn.clicked.connect(lambda checked, r=row: self.schedule_post_from_table(r))
                self.campaigns_table.setCellWidget(row, 4, btn)

    def load_partnerships(self):
        self.partnerships_table.setRowCount(0)
        for partner in self.partnership_manager.get_partners_by_status():
            row = self.partnerships_table.rowCount()
            self.partnerships_table.insertRow(row)
            self.partnerships_table.setItem(row, 0, QTableWidgetItem(str(partner['id'])))
            self.partnerships_table.setItem(row, 1, QTableWidgetItem(partner['name']))
            self.partnerships_table.setItem(row, 2, QTableWidgetItem(partner['industry']))
            self.partnerships_table.setItem(row, 3, QTableWidgetItem(partner['status']))
            if partner['status'] == 'Potential':
                btn = QPushButton("Propose")
                btn.clicked.connect(lambda checked, pid=partner['id']: self.propose_from_table(pid))
                self.partnerships_table.setCellWidget(row, 4, btn)

    def load_analytics(self):
        # Summary text
        summary = self.analytics_manager.get_campaign_performance()
        if isinstance(summary, str):
            self.analytics_summary.setText(summary)
        else:
            self.analytics_summary.setText(f"Campaign Performance Summary:\n{summary.to_string()}")
        
        # Channel performance
        self.channel_table.setRowCount(0)
        performance = self.analytics_manager.get_channel_performance()
        if isinstance(performance, dict):
            for channel, metrics in performance.items():
                if isinstance(metrics, pd.DataFrame):
                    row = self.channel_table.rowCount()
                    self.channel_table.insertRow(row)
                    self.channel_table.setItem(row, 0, QTableWidgetItem(channel))
                    if 'mean' in metrics.index:
                        mean = metrics.loc['mean']
                        self.channel_table.setItem(row, 1, QTableWidgetItem(str(mean.get('impressions', 0))))
                        self.channel_table.setItem(row, 2, QTableWidgetItem(str(mean.get('clicks', 0))))
                        self.channel_table.setItem(row, 3, QTableWidgetItem(str(mean.get('conversions', 0))))
                        self.channel_table.setItem(row, 4, QTableWidgetItem(f"{mean.get('CTR', 0):.2f}%"))
                        self.channel_table.setItem(row, 5, QTableWidgetItem(f"${mean.get('CPC', 0):.2f}"))
        
        # Recommendations
        recs = self.analytics_manager.recommend_strategy_adjustment()
        self.recommendations_label.setText("Recommendations:\n" + "\n".join(recs))

    def add_content(self):
        content_idea = self.content_input.text()
        platforms_text = self.platforms_input.text()
        visual_desc = self.visual_input.text()
        if not content_idea or not platforms_text:
            QMessageBox.warning(self, "Input Error", "Content idea and platforms are required.")
            return
        platforms = [p.strip() for p in platforms_text.split(',')]
        self.campaign_manager.add_content_to_plan(content_idea, platforms, visual_desc)
        self.content_input.clear()
        self.platforms_input.clear()
        self.visual_input.clear()
        self.load_campaigns()
        QMessageBox.information(self, "Success", "Content added to plan.")

    def schedule_post(self):
        content_id_text = self.schedule_id_input.text()
        if not content_id_text.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid content ID.")
            return
        content_id = int(content_id_text)
        if content_id >= len(self.campaign_manager.content_plan):
            QMessageBox.warning(self, "Input Error", "Content ID does not exist.")
            return
        post_date = self.schedule_date_input.date().toPython()
        post_time = datetime(post_date.year, post_date.month, post_date.day)
        self.campaign_manager.schedule_post(content_id, post_time)
        self.schedule_id_input.clear()
        self.load_campaigns()
        QMessageBox.information(self, "Success", f"Post scheduled for {post_date}.")

    def schedule_post_from_table(self, row):
        content_id = int(self.campaigns_table.item(row, 0).text())
        post_time = datetime.now()
        self.campaign_manager.schedule_post(content_id, post_time)
        self.load_campaigns()
        QMessageBox.information(self, "Success", "Post scheduled.")

    def add_partner(self):
        name = self.partner_name_input.text()
        industry = self.partner_industry_input.text()
        contact = self.partner_contact_input.text()
        value = self.partner_value_input.text()
        if not name or not industry:
            QMessageBox.warning(self, "Input Error", "Name and industry are required.")
            return
        self.partnership_manager.add_potential_partner(name, industry, contact, value)
        self.partner_name_input.clear()
        self.partner_industry_input.clear()
        self.partner_contact_input.clear()
        self.partner_value_input.clear()
        self.load_partnerships()
        QMessageBox.information(self, "Success", "Partner added.")

    def propose_partnership(self):
        partner_id_text = self.proposal_id_input.text()
        if not partner_id_text.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid partner ID.")
            return
        partner_id = int(partner_id_text)
        proposal_type = self.proposal_type_input.text()
        details = self.proposal_details_input.text()
        if not proposal_type or not details:
            QMessageBox.warning(self, "Input Error", "Proposal type and details are required.")
            return
        try:
            self.partnership_manager.propose_partnership(partner_id, proposal_type, details)
            self.proposal_id_input.clear()
            self.proposal_type_input.clear()
            self.proposal_details_input.clear()
            self.load_partnerships()
            QMessageBox.information(self, "Success", "Partnership proposed.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def propose_from_table(self, partner_id):
        proposal_type = "Co-Marketing"
        details = f"Proposing collaboration with {partner_id}"
        self.partnership_manager.propose_partnership(partner_id, proposal_type, details)
        self.load_partnerships()
        QMessageBox.information(self, "Success", "Partnership proposed.")

    def record_metrics(self):
        channel = self.channel_input.text()
        try:
            impressions = int(self.impressions_input.text())
            clicks = int(self.clicks_input.text())
            conversions = int(self.conversions_input.text())
            cost = float(self.cost_input.text())
            if channel not in self.analytics_manager.channel_metrics:
                QMessageBox.warning(self, "Input Error", f"Invalid channel: {channel}")
                return
            self.analytics_manager.update_channel_metrics(channel, impressions, clicks, conversions, cost)
            self.channel_input.clear()
            self.impressions_input.clear()
            self.clicks_input.clear()
            self.conversions_input.clear()
            self.cost_input.clear()
            self.load_analytics()
            QMessageBox.information(self, "Success", "Metrics recorded.")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers for metrics.")

    def visualize_performance(self):
        self.analytics_manager.visualize_channel_performance()
        QMessageBox.information(self, "Visualization", "Performance charts displayed. Check the plots for details.")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dashboard = MarketingDashboard()
    dashboard.show()
    sys.exit(app.exec())
