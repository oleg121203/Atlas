"""
Workflow Analytics Integration Module

This module integrates workflow analytics with user satisfaction data to provide
correlations between performance metrics and user feedback.
"""

from workflow_analytics import WorkflowAnalytics
from user_satisfaction import UserSatisfactionMonitor
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

class AnalyticsIntegration:
    def __init__(self, workflow_analytics: WorkflowAnalytics, satisfaction_monitor: UserSatisfactionMonitor):
        self.workflow_analytics = workflow_analytics
        self.satisfaction_monitor = satisfaction_monitor

    def correlate_performance_satisfaction(self, workflow_id: str, days: int = 30):
        """
        Correlate workflow performance metrics with user satisfaction data over a specified period.
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get workflow performance data
        wf_executions = self.workflow_analytics.execution_data[
            (self.workflow_analytics.execution_data['workflow_id'] == workflow_id) &
            (self.workflow_analytics.execution_data['start_time'] >= cutoff_date)
        ]

        # Get user satisfaction data
        wf_feedback = self.satisfaction_monitor.feedback_data[
            (self.satisfaction_monitor.feedback_data['workflow_id'] == workflow_id) &
            (self.satisfaction_monitor.feedback_data['timestamp'] >= cutoff_date)
        ]

        if wf_executions.empty or wf_feedback.empty:
            print(f"Insufficient data to correlate performance and satisfaction for {workflow_id}")
            return None

        # Aggregate performance data by day
        wf_executions['date'] = wf_executions['start_time'].dt.date
        daily_performance = wf_executions.groupby('date').agg({
            'success': 'mean',
            'duration': 'mean'
        }).reset_index()
        daily_performance['success_rate'] = daily_performance['success'] * 100

        # Aggregate satisfaction data by day
        wf_feedback['date'] = wf_feedback['timestamp'].dt.date
        daily_satisfaction = wf_feedback.groupby('date').agg({
            'nps_score': lambda x: x[x > 0].mean(),
            'sentiment': 'mean'
        }).reset_index()

        # Merge the datasets
        merged_data = pd.merge(daily_performance, daily_satisfaction, on='date', how='outer')
        merged_data = merged_data.sort_values('date')

        # Fill missing values with forward fill
        merged_data = merged_data.fillna(method='ffill').fillna(method='bfill')

        # Calculate correlations
        correlation_matrix = merged_data[['success_rate', 'duration', 'nps_score', 'sentiment']].corr()

        return {
            'data': merged_data,
            'correlations': correlation_matrix
        }

    def visualize_correlation_dashboard(self, workflow_id: str, days: int = 30):
        """
        Visualize correlations between workflow performance and user satisfaction.
        """
        correlation_result = self.correlate_performance_satisfaction(workflow_id, days)
        if correlation_result is None:
            return

        merged_data = correlation_result['data']
        correlation_matrix = correlation_result['correlations']

        fig = plt.figure(figsize=(15, 10))

        # Plot success rate vs NPS
        ax1 = fig.add_subplot(2, 2, 1)
        ax1_twin = ax1.twinx()
        merged_data.plot(x='date', y='success_rate', ax=ax1, color='blue', marker='o', label='Success Rate (%)')
        merged_data.plot(x='date', y='nps_score', ax=ax1_twin, color='green', marker='s', label='NPS Score')
        ax1.set_title(f'Success Rate vs NPS Score for {workflow_id}')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Success Rate (%)', color='blue')
        ax1_twin.set_ylabel('NPS Score', color='green')
        ax1.grid(True)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)

        # Plot duration vs sentiment
        ax2 = fig.add_subplot(2, 2, 2)
        ax2_twin = ax2.twinx()
        merged_data.plot(x='date', y='duration', ax=ax2, color='red', marker='o', label='Duration (s)')
        merged_data.plot(x='date', y='sentiment', ax=ax2_twin, color='purple', marker='s', label='Sentiment')
        ax2.set_title(f'Duration vs Sentiment for {workflow_id}')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Duration (seconds)', color='red')
        ax2_twin.set_ylabel('Sentiment Score', color='purple')
        ax2.grid(True)
        for tick in ax2.get_xticklabels():
            tick.set_rotation(45)

        # Correlation heatmap
        ax3 = fig.add_subplot(2, 2, 3)
        import seaborn as sns
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax3)
        ax3.set_title('Correlation Matrix')

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    # Demo usage
    from workflow_analytics_demo import create_sample_data
    wf_analytics = WorkflowAnalytics()
    wf_analytics = create_sample_data(wf_analytics)
    satisfaction = UserSatisfactionMonitor()
    
    # Add sample satisfaction data
    wf_ids = ['DataPipeline', 'MLTraining', 'ReportGeneration']
    for wf in wf_ids:
        for i in range(20):
            satisfaction.collect_nps_score(f'user{i}', wf, random.randint(0, 10))
            if random.random() < 0.5:
                feedback = random.choice(['Great workflow!', 'Too slow.', 'Needs improvement.', 'Very efficient!'])
                satisfaction.collect_feedback(f'user{i}', wf, feedback)
    
    # Create integration instance
    integration = AnalyticsIntegration(wf_analytics, satisfaction)
    
    # Visualize correlations for a workflow
    integration.visualize_correlation_dashboard('DataPipeline')
