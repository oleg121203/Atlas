"""
Workflow Optimization Module

This module provides intelligent recommendations for workflow optimization based on
historical performance data, user feedback, and system constraints.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import networkx as nx
from sklearn.cluster import KMeans
from workflow_analytics import WorkflowAnalytics

class WorkflowOptimizer:
    def __init__(self, analytics: WorkflowAnalytics):
        self.analytics = analytics
        self.graphs: Dict[str, nx.DiGraph] = {}
        self.optimization_history: Dict[str, List[Dict]] = {}

    def build_workflow_graph(self, workflow_id: str, days: int = 30) -> nx.DiGraph:
        """
        Build a directed graph representation of the workflow based on step execution data.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        wf_steps = self.analytics.step_data[
            (self.analytics.step_data['workflow_id'] == workflow_id) &
            (self.analytics.step_data['start_time'] >= cutoff_date)
        ]

        if wf_steps.empty:
            print(f"No step data available for workflow {workflow_id} in the last {days} days")
            return nx.DiGraph()

        G = nx.DiGraph()
        executions = wf_steps['execution_id'].unique()

        for exec_id in executions:
            exec_steps = wf_steps[wf_steps['execution_id'] == exec_id].sort_values('start_time')
            for i in range(len(exec_steps) - 1):
                current_step = exec_steps.iloc[i]['step_id']
                next_step = exec_steps.iloc[i + 1]['step_id']
                if not G.has_node(current_step):
                    G.add_node(current_step, name=exec_steps.iloc[i]['step_name'])
                if not G.has_node(next_step):
                    G.add_node(next_step, name=exec_steps.iloc[i + 1]['step_name'])
                if G.has_edge(current_step, next_step):
                    G[current_step][next_step]['weight'] += 1
                    G[current_step][next_step]['duration'] += exec_steps.iloc[i]['duration']
                else:
                    G.add_edge(current_step, next_step, weight=1, duration=exec_steps.iloc[i]['duration'])

        # Normalize durations by number of occurrences
        for edge in G.edges(data=True):
            u, v, data = edge
            data['avg_duration'] = data['duration'] / data['weight']

        self.graphs[workflow_id] = G
        return G

    def identify_critical_path(self, workflow_id: str) -> List[str]:
        """
        Identify the critical path in the workflow graph based on average step durations.
        """
        if workflow_id not in self.graphs:
            self.build_workflow_graph(workflow_id)
        G = self.graphs.get(workflow_id, nx.DiGraph())

        if not G.nodes:
            return []

        # Find start and end nodes (nodes with no incoming or outgoing edges)
        start_nodes = [n for n, d in G.in_degree() if d == 0]
        end_nodes = [n for n, d in G.out_degree() if d == 0]

        if not start_nodes or not end_nodes:
            print(f"Workflow {workflow_id} has no clear start or end nodes")
            return []

        # For simplicity, use the first start and end node
        start_node = start_nodes[0]
        end_node = end_nodes[0]

        # Calculate longest path based on average duration
        all_paths = list(nx.all_simple_paths(G, start_node, end_node))
        if not all_paths:
            return []

        critical_path = max(
            all_paths,
            key=lambda path: sum(G[path[i]][path[i+1]]['avg_duration'] for i in range(len(path)-1)),
            default=[]
        )

        return critical_path

    def cluster_executions(self, workflow_id: str, days: int = 30, n_clusters: int = 3) -> Dict[str, Any]:
        """
        Cluster workflow executions based on performance characteristics to identify patterns.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        wf_executions = self.analytics.execution_data[
            (self.analytics.execution_data['workflow_id'] == workflow_id) &
            (self.analytics.execution_data['start_time'] >= cutoff_date)
        ]

        if len(wf_executions) < n_clusters:
            print(f"Insufficient execution data for clustering in workflow {workflow_id}")
            return {'labels': [], 'centers': [], 'execution_ids': []}

        # Prepare features for clustering
        features = wf_executions[['duration']].copy()
        features['success'] = wf_executions['success'].astype(int)
        features['hour'] = wf_executions['start_time'].dt.hour
        features['day_of_week'] = wf_executions['start_time'].dt.weekday

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features)

        return {
            'labels': labels.tolist(),
            'centers': kmeans.cluster_centers_.tolist(),
            'execution_ids': wf_executions['execution_id'].tolist()
        }

    def recommend_optimizations(self, workflow_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate intelligent recommendations for workflow optimization.
        """
        recommendations = []

        # Get performance metrics
        metrics = self.analytics.get_performance_metrics(workflow_id, days)
        if metrics['total_executions'] == 0:
            return [{'type': 'data_insufficient', 'description': 'Insufficient data for recommendations'}]

        # Check success rate
        if metrics['success_rate'] < 90.0:
            recommendations.append({
                'type': 'reliability',
                'priority': 'high',
                'description': f"Workflow success rate is {metrics['success_rate']:.1f}%. Investigate common errors.",
                'details': metrics['common_errors']
            })

        # Identify critical path for potential parallelization or optimization
        critical_path = self.identify_critical_path(workflow_id)
        if critical_path:
            path_steps = [self.graphs[workflow_id].nodes[step]['name'] for step in critical_path]
            total_duration = sum(
                self.graphs[workflow_id][critical_path[i]][critical_path[i+1]]['avg_duration'] 
                for i in range(len(critical_path)-1)
            )
            recommendations.append({
                'type': 'critical_path',
                'priority': 'medium',
                'description': f"Critical path takes {total_duration:.1f}s on average. Consider optimizing: {', '.join(path_steps)}",
                'steps': path_steps
            })

        # Check for high variance in execution duration
        if metrics['max_duration'] > metrics['average_duration'] * 1.5:
            recommendations.append({
                'type': 'performance_variance',
                'priority': 'medium',
                'description': f"High variance in execution duration (avg: {metrics['average_duration']:.1f}s, max: {metrics['max_duration']:.1f}s). Investigate outliers.",
                'details': {'avg_duration': metrics['average_duration'], 'max_duration': metrics['max_duration']}
            })

        # Cluster executions to identify patterns
        clustering = self.cluster_executions(workflow_id, days)
        if clustering['labels']:
            recommendations.append({
                'type': 'execution_patterns',
                'priority': 'low',
                'description': f"Identified {len(set(clustering['labels']))} distinct execution patterns. Review clusters for optimization opportunities.",
                'details': {'centers': clustering['centers']}
            })

        # Record optimization recommendations for history
        if workflow_id not in self.optimization_history:
            self.optimization_history[workflow_id] = []
        self.optimization_history[workflow_id].append({
            'timestamp': datetime.now(),
            'recommendations': recommendations
        })

        return recommendations if recommendations else [{'type': 'no_issues', 'description': 'No significant optimization opportunities identified at this time.'}]

    def evaluate_optimization_impact(self, workflow_id: str, optimization_id: str, before_days: int = 30, after_days: int = 30) -> Dict[str, Any]:
        """
        Evaluate the impact of a specific optimization by comparing performance metrics before and after.
        """
        # This would ideally use a timestamp or ID for the optimization event
        # For simplicity, we'll just compare recent performance with older performance
        now = datetime.now()
        before_cutoff = now - timedelta(days=before_days + after_days)
        after_cutoff = now - timedelta(days=after_days)

        before_data = self.analytics.execution_data[
            (self.analytics.execution_data['workflow_id'] == workflow_id) &
            (self.analytics.execution_data['start_time'] >= before_cutoff) &
            (self.analytics.execution_data['start_time'] < after_cutoff)
        ]

        after_data = self.analytics.execution_data[
            (self.analytics.execution_data['workflow_id'] == workflow_id) &
            (self.analytics.execution_data['start_time'] >= after_cutoff) &
            (self.analytics.execution_data['start_time'] <= now)
        ]

        before_metrics = self.analytics.get_performance_metrics(workflow_id, days=before_days + after_days)
        after_metrics = self.analytics.get_performance_metrics(workflow_id, days=after_days)

        return {
            'before': {
                'success_rate': before_metrics['success_rate'],
                'avg_duration': before_metrics['average_duration'],
                'total_executions': before_metrics['total_executions'],
                'time_period': f"{before_days + after_days} days before optimization"
            },
            'after': {
                'success_rate': after_metrics['success_rate'],
                'avg_duration': after_metrics['average_duration'],
                'total_executions': after_metrics['total_executions'],
                'time_period': f"{after_days} days after optimization"
            },
            'impact': {
                'success_rate_change': after_metrics['success_rate'] - before_metrics['success_rate'],
                'duration_change': after_metrics['average_duration'] - before_metrics['average_duration']
            }
        }

if __name__ == '__main__':
    from workflow_analytics_demo import create_sample_data
    analytics = WorkflowAnalytics()
    analytics = create_sample_data(analytics)
    optimizer = WorkflowOptimizer(analytics)
    
    wf_id = 'DataPipeline'
    print(f"Building workflow graph for {wf_id}...")
    graph = optimizer.build_workflow_graph(wf_id)
    print(f"Nodes: {graph.nodes}")
    print(f"Edges: {graph.edges}")
    
    print(f"\nIdentifying critical path for {wf_id}...")
    critical_path = optimizer.identify_critical_path(wf_id)
    print(f"Critical Path: {critical_path}")
    
    print(f"\nClustering executions for {wf_id}...")
    clustering = optimizer.cluster_executions(wf_id)
    print(f"Clustering results: {len(clustering['labels'])} executions clustered")
    
    print(f"\nGenerating optimization recommendations for {wf_id}...")
    recommendations = optimizer.recommend_optimizations(wf_id)
    for rec in recommendations:
        print(f"- {rec['type']}: {rec['description']}")
        if 'details' in rec:
            print(f"  Details: {rec['details']}")
