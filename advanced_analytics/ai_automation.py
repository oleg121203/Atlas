"""
AI-Driven Automation Module

This module provides functionality for implementing AI-driven automation
for task management and workflow optimization.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime
import re
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

class AIAutomation:
    def __init__(self, data_source: str):
        """
        Initialize the AI Automation system.

        Args:
            data_source (str): The source of data for automation (e.g., database connection string).
        """
        self.data_source = data_source
        self.task_data = pd.DataFrame()
        self.model = None

    def load_task_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Load task data for AI processing within a specified date range.

        Args:
            start_date (datetime): The start date for data collection.
            end_date (datetime): The end date for data collection.

        Returns:
            pd.DataFrame: DataFrame containing loaded task data.
        """
        # Placeholder for actual data loading logic
        date_range = pd.date_range(start=start_date, end=end_date, freq='h')
        num_rows = len(date_range)
        self.task_data = pd.DataFrame({
            'task_id': range(num_rows),
            'creation_time': date_range,
            'due_time': [date_range[i] + pd.Timedelta(hours=np.random.randint(1, 48)) for i in range(num_rows)],
            'priority': np.random.choice(['low', 'medium', 'high'], num_rows),
            'duration_hours': np.random.normal(2, 1, num_rows),
            'user_id': np.random.randint(1, 100, num_rows),
            'description': [f"Task {i}" for i in range(num_rows)]
        })
        return self.task_data

    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize tasks based on AI-driven clustering and feature analysis.
        Utilizes unsupervised learning to group tasks and assign priority scores.

        Args:
            tasks (List[Dict[str, Any]]): List of task dictionaries with features.

        Returns:
            List[Dict[str, Any]]: Prioritized list of tasks with updated priority fields.
        """
        if not tasks:
            return []

        try:
            # Extract features for clustering
            feature_matrix = []
            for task in tasks:
                features = []
                # Convert due_date to a numeric feature if possible
                due_str = task.get('due_date', 'not specified')
                if due_str != 'not specified':
                    try:
                        due_date = parser.parse(due_str, fuzzy=True)
                        days_until_due = (due_date - datetime.now()).days
                        features.append(max(0, 15 - days_until_due))  # Higher urgency for closer deadlines
                    except ValueError:
                        if due_str.lower() == 'today':
                            features.append(15)  # Highest urgency for 'today'
                        elif due_str.lower() == 'tomorrow':
                            features.append(10)  # High urgency for 'tomorrow'
                        else:
                            features.append(5)  # Default urgency for unparseable dates
                else:
                    features.append(3)  # Lower urgency for tasks without due dates

                # Add feature based on task name length (longer might indicate more complexity)
                features.append(len(task.get('name', '')) / 10.0)

                # Add feature for source (text-created tasks might need review)
                features.append(1.0 if task.get('created_from_text', False) else 0.5)

                feature_matrix.append(features)

            # Apply KMeans clustering to group tasks by urgency and complexity
            n_clusters = min(len(tasks), 3)  # Limit clusters to 3 or number of tasks if fewer
            if n_clusters < 2:
                # Assign default priority if too few tasks for clustering
                for task in tasks:
                    task['priority'] = 'high' if feature_matrix[0][0] > 10 else 'medium'
                return sorted(tasks, key=lambda x: x['priority'], reverse=True)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(feature_matrix)

            # Calculate centroid urgency (based on first feature - due date urgency)
            centroid_urgency = []
            for i in range(n_clusters):
                cluster_points = [feature_matrix[j][0] for j in range(len(tasks)) if clusters[j] == i]
                urgency = sum(cluster_points) / len(cluster_points) if cluster_points else 0
                centroid_urgency.append((i, urgency))

            # Sort clusters by urgency (higher urgency first)
            cluster_priority = {cluster_id: rank for rank, (cluster_id, _) in enumerate(sorted(centroid_urgency, key=lambda x: x[1], reverse=True))}

            # Assign priorities based on cluster urgency ranking
            priority_mapping = {0: 'high', 1: 'medium', 2: 'low'}
            for i, task in enumerate(tasks):
                cluster_rank = cluster_priority[clusters[i]]
                task['priority'] = priority_mapping.get(cluster_rank, 'medium')

            # Sort tasks by cluster urgency (high priority first)
            return sorted(tasks, key=lambda x: ['high', 'medium', 'low'].index(x['priority']))
        except Exception as e:
            logger.error(f"Error prioritizing tasks: {e}")
            # Fallback to default priority if error occurs
            for task in tasks:
                task['priority'] = 'medium'
            return tasks

    def extract_task_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract task information from natural language text.

        Args:
            text (str): Natural language text input.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing task information if extracted, None otherwise.
        """
        task_name = None
        due_date = None
        text_lower = text.lower()

        # Keywords that indicate a task
        task_indicators = ["create a task", "make a task", "do a task", "complete a task", "need to", "have to", "got to"]
        due_indicators = ["due", "by", "for", "on", "at", "today", "tomorrow"]

        # Check if any task indicator is in the text
        for indicator in task_indicators:
            if indicator in text_lower:
                # Split by the indicator and take the part after it
                parts = text_lower.split(indicator, 1)
                if len(parts) > 1:
                    task_part = parts[1].strip()
                    # Check for due date indicators in the task part
                    for due_indicator in due_indicators:
                        if due_indicator in task_part:
                            due_split = task_part.split(due_indicator, 1)
                            task_name = due_split[0].strip(": -")
                            if len(due_split) > 1 and due_indicator not in ["today", "tomorrow"]:
                                due_date_lower = due_split[1].strip()
                                # Find the original text for due date to preserve capitalization
                                start_index_due = text_lower.find(due_date_lower)
                                if start_index_due != -1:
                                    due_date = text[start_index_due:start_index_due + len(due_date_lower)]
                                else:
                                    due_date = due_date_lower
                            else:
                                due_date = due_indicator
                                # Find the original text for due date to preserve capitalization
                                start_index_due = text_lower.find(due_date)
                                if start_index_due != -1:
                                    due_date = text[start_index_due:start_index_due + len(due_date)]
                            break
                    if not task_name:
                        task_name = task_part.strip(": -")
                break

        if task_name:
            # Find the original text for the task name to preserve capitalization
            start_index = text_lower.find(task_name)
            if start_index != -1:
                task_name = text[start_index:start_index + len(task_name)]
            return {
                'name': task_name,
                'due_date': due_date if due_date else 'not specified',
                'priority': 'medium',  # Default priority
                'created_from_text': True
            }
        return None

    def recommend_workflow(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Recommend workflow optimizations based on user behavior and task patterns.
        Uses historical data to suggest improvements in task grouping and scheduling.

        Args:
            user_id (int): User ID to analyze behavior for personalized recommendations.

        Returns:
            List[Dict[str, Any]]: List of workflow optimization recommendations.
        """
        if self.task_data.empty:
            return []

        try:
            user_tasks = self.task_data[self.task_data['user_id'] == user_id]
            if user_tasks.empty:
                return []

            recommendations = []

            # Analyze task completion patterns
            completion_rate = user_tasks['completed'].mean() if 'completed' in user_tasks.columns else 0
            if completion_rate < 0.7:  # Suggest improvements if completion rate is low
                recommendations.append({
                    'recommendation': 'Batch similar tasks together',
                    'confidence': 0.75,
                    'reason': 'Low completion rate detected. Grouping similar tasks may improve focus and efficiency.'
                })

            # Check for overdue tasks
            if 'due_time' in user_tasks.columns:
                overdue_count = len(user_tasks[user_tasks['due_time'] < datetime.now()])
                if overdue_count > len(user_tasks) * 0.3:  # More than 30% overdue
                    recommendations.append({
                        'recommendation': 'Set realistic deadlines',
                        'confidence': 0.8,
                        'reason': 'High number of overdue tasks. Consider allocating more time or reducing task load.'
                    })

            # Analyze task duration vs estimated duration if available
            if 'duration_hours' in user_tasks.columns and 'estimated_duration_hours' in user_tasks.columns:
                avg_duration_diff = (user_tasks['duration_hours'] - user_tasks['estimated_duration_hours']).mean()
                if avg_duration_diff > 1.0:  # Tasks take significantly longer than estimated
                    recommendations.append({
                        'recommendation': 'Improve task estimation',
                        'confidence': 0.7,
                        'reason': 'Tasks consistently take longer than estimated. Consider breaking tasks into smaller units.'
                    })

            # Suggest automation for repetitive tasks
            if len(user_tasks['name'].str.lower().value_counts()) < len(user_tasks) * 0.5:  # Many repeated task names
                recommendations.append({
                    'recommendation': 'Automate repetitive tasks',
                    'confidence': 0.65,
                    'reason': 'Detected multiple similar tasks. Automation or templates could save time.'
                })

            return recommendations
        except Exception as e:
            logger.error(f"Error generating workflow recommendations: {e}")
            return []
