"""
Workflow Execution Analytics Module

This module provides comprehensive analytics for workflow execution, including performance metrics,
bottleneck visualization, customizable dashboards, comparative analytics, and predictive failure analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Optional

class WorkflowAnalytics:
    def __init__(self):
        self.execution_data = pd.DataFrame(columns=['workflow_id', 'execution_id', 'start_time', 'end_time', 
                                                    'duration', 'success', 'error_message', 'steps'])
        self.step_data = pd.DataFrame(columns=['workflow_id', 'execution_id', 'step_id', 'step_name', 
                                               'start_time', 'end_time', 'duration', 'success', 'error_message'])
        self.predictive_model = IsolationForest(contamination=0.1, random_state=42)

    def record_execution(self, workflow_id: str, execution_id: str, start_time: datetime, end_time: datetime, 
                         success: bool, error_message: str = '', steps: List[Dict] = None):
        """
        Record details of a workflow execution.
        """
        duration = (end_time - start_time).total_seconds()
        new_entry = {
            'workflow_id': workflow_id,
            'execution_id': execution_id,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'success': success,
            'error_message': error_message,
            'steps': steps or []
        }
        self.execution_data = pd.concat([self.execution_data, pd.DataFrame([new_entry])], ignore_index=True)

        # Record individual step data if provided
        if steps:
            for step in steps:
                step_duration = (step['end_time'] - step['start_time']).total_seconds() if step.get('end_time') else 0
                step_entry = {
                    'workflow_id': workflow_id,
                    'execution_id': execution_id,
                    'step_id': step['step_id'],
                    'step_name': step.get('step_name', step['step_id']),
                    'start_time': step['start_time'],
                    'end_time': step.get('end_time'),
                    'duration': step_duration,
                    'success': step.get('success', False),
                    'error_message': step.get('error_message', '')
                }
                self.step_data = pd.concat([self.step_data, pd.DataFrame([step_entry])], ignore_index=True)

    def get_performance_metrics(self, workflow_id: Optional[str] = None, days: int = 30) -> Dict:
        """
        Calculate detailed performance metrics for workflows.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        if workflow_id:
            wf_executions = self.execution_data[
                (self.execution_data['workflow_id'] == workflow_id) & 
                (self.execution_data['start_time'] >= cutoff_date)
            ]
        else:
            wf_executions = self.execution_data[self.execution_data['start_time'] >= cutoff_date]

        if wf_executions.empty:
            return {
                'total_executions': 0,
                'success_rate': 0,
                'average_duration': 0,
                'median_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'error_count': 0,
                'common_errors': []
            }

        total_executions = len(wf_executions)
        success_count = len(wf_executions[wf_executions['success'] == True])
        error_executions = wf_executions[wf_executions['success'] == False]
        error_count = len(error_executions)
        common_errors = error_executions['error_message'].value_counts().head(3).to_dict()

        return {
            'total_executions': total_executions,
            'success_rate': (success_count / total_executions) * 100 if total_executions > 0 else 0,
            'average_duration': wf_executions['duration'].mean(),
            'median_duration': wf_executions['duration'].median(),
            'min_duration': wf_executions['duration'].min(),
            'max_duration': wf_executions['duration'].max(),
            'error_count': error_count,
            'common_errors': list(common_errors.items())
        }

    def visualize_bottlenecks_heatmap(self, workflow_id: str, days: int = 30):
        """
        Visualize workflow bottlenecks using a heatmap of step durations.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        wf_steps = self.step_data[
            (self.step_data['workflow_id'] == workflow_id) & 
            (self.step_data['start_time'] >= cutoff_date)
        ]

        if wf_steps.empty:
            print(f"No step data available for workflow {workflow_id} in the last {days} days")
            return

        # Pivot table for heatmap: step_name vs execution_id with duration as value
        pivot_data = wf_steps.pivot_table(
            values='duration', 
            index='step_name', 
            columns='execution_id', 
            aggfunc='mean'
        )

        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_data, cmap='YlOrRd', annot=True, fmt='.1f')
        plt.title(f'Workflow {workflow_id} Step Duration Heatmap')
        plt.xlabel('Execution ID')
        plt.ylabel('Step Name')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def customizable_dashboard(self, workflow_ids: Optional[List[str]] = None, days: int = 30, export: bool = False):
        """
        Create a customizable dashboard for workflow analytics with export capability.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        if workflow_ids:
            wf_executions = self.execution_data[
                (self.execution_data['workflow_id'].isin(workflow_ids)) & 
                (self.execution_data['start_time'] >= cutoff_date)
            ]
        else:
            wf_executions = self.execution_data[self.execution_data['start_time'] >= cutoff_date]

        if wf_executions.empty:
            print(f"No execution data available for the selected workflows in the last {days} days")
            return None

        fig = plt.figure(figsize=(15, 10))

        # Success Rate by Workflow
        ax1 = fig.add_subplot(2, 2, 1)
        success_rates = wf_executions.groupby('workflow_id')['success'].mean() * 100
        success_rates.plot(kind='bar', color='skyblue', ax=ax1)
        ax1.set_title('Success Rate by Workflow (%)')
        ax1.set_ylabel('Success Rate')
        ax1.set_ylim(0, 100)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)

        # Average Duration by Workflow
        ax2 = fig.add_subplot(2, 2, 2)
        avg_durations = wf_executions.groupby('workflow_id')['duration'].mean()
        avg_durations.plot(kind='bar', color='lightgreen', ax=ax2)
        ax2.set_title('Average Duration by Workflow (seconds)')
        ax2.set_ylabel('Average Duration')
        for tick in ax2.get_xticklabels():
            tick.set_rotation(45)

        # Execution Trend
        ax3 = fig.add_subplot(2, 2, 3)
        daily_executions = wf_executions.groupby([wf_executions['start_time'].dt.date, 'workflow_id']).size().unstack()
        daily_executions.plot(kind='line', marker='o', ax=ax3)
        ax3.set_title('Daily Execution Count by Workflow')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Execution Count')
        ax3.grid(True)
        for tick in ax3.get_xticklabels():
            tick.set_rotation(45)

        # Error Distribution
        ax4 = fig.add_subplot(2, 2, 4)
        error_counts = wf_executions[wf_executions['success'] == False]['workflow_id'].value_counts()
        if not error_counts.empty:
            error_counts.plot(kind='bar', color='salmon', ax=ax4)
            ax4.set_title('Error Count by Workflow')
            ax4.set_ylabel('Error Count')
            for tick in ax4.get_xticklabels():
                tick.set_rotation(45)
        else:
            ax4.text(0.5, 0.5, 'No Errors Recorded', horizontalalignment='center', verticalalignment='center')
            ax4.set_title('Error Count by Workflow')

        plt.tight_layout()
        plt.show()

        # Export data if requested
        if export:
            export_data = wf_executions.copy()
            export_data.to_csv(f'workflow_analytics_{datetime.now().strftime("%Y%m%d")}.csv', index=False)
            print(f"Data exported to workflow_analytics_{datetime.now().strftime('%Y%m%d')}.csv")

        return wf_executions

    def comparative_analytics(self, entity_type: str = 'workflow', entity_ids: Optional[List[str]] = None, 
                              days: int = 30) -> pd.DataFrame:
        """
        Compare workflow performance across different entities (workflows, teams, or users).
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        relevant_executions = self.execution_data[self.execution_data['start_time'] >= cutoff_date]

        if entity_ids:
            relevant_executions = relevant_executions[relevant_executions['workflow_id'].isin(entity_ids)]

        if relevant_executions.empty:
            print(f"No data available for comparative analytics in the last {days} days")
            return pd.DataFrame()

        # For simplicity, we're using workflow_id as the entity for comparison
        # In a real system, you'd join with user/team metadata
        comparison_metrics = relevant_executions.groupby('workflow_id').agg({
            'success': 'mean',
            'duration': ['mean', 'median', 'min', 'max'],
            'execution_id': 'count'
        }).round(2)

        comparison_metrics.columns = ['success_rate', 'avg_duration', 'median_duration', 
                                     'min_duration', 'max_duration', 'total_executions']
        comparison_metrics['success_rate'] = comparison_metrics['success_rate'] * 100

        return comparison_metrics.reset_index()

    def train_predictive_model(self):
        """
        Train the predictive model for potential workflow failures based on historical data.
        """
        if len(self.execution_data) < 10:
            print("Insufficient data to train predictive model. Need at least 10 execution records.")
            return False

        # Prepare features for anomaly detection
        features = self.execution_data[['duration']].copy()
        features['success'] = self.execution_data['success'].astype(int)
        # Add more features if available, e.g., time of day, day of week
        features['hour'] = self.execution_data['start_time'].dt.hour
        features['day_of_week'] = self.execution_data['start_time'].dt.dayofweek

        # Train the model
        self.predictive_model.fit(features)
        print("Predictive model trained for anomaly detection")
        return True

    def predict_workflow_failure(self, workflow_id: str, current_duration: float, 
                                execution_time: datetime) -> Dict[str, float]:
        """
        Predict potential workflow failure based on current execution parameters.
        """
        if not hasattr(self.predictive_model, 'decision_function'):
            print("Predictive model not trained yet. Call train_predictive_model first.")
            return {'anomaly_score': 0.0, 'failure_probability': 0.0}

        # Prepare features for the current execution
        features = pd.DataFrame({
            'duration': [current_duration],
            'success': [1],  # Placeholder, will be ignored in prediction
            'hour': [execution_time.hour],
            'day_of_week': [execution_time.weekday()]
        })

        # Get anomaly score (negative values indicate anomalies in IsolationForest)
        anomaly_score = self.predictive_model.decision_function(features)[0]
        # Convert to a probability-like score (this is a simple transformation, could be improved)
        failure_prob = max(0, -anomaly_score * 0.5)  

        return {
            'anomaly_score': float(anomaly_score),
            'failure_probability': min(1.0, float(failure_prob))
        }
