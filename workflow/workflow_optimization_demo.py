"""
Demo script for WorkflowOptimizer class

This script demonstrates the usage of WorkflowOptimizer with sample workflow data.
"""

from workflow_analytics import WorkflowAnalytics
from workflow_analytics_demo import create_sample_data
from workflow_optimization import WorkflowOptimizer

if __name__ == "__main__":
    # Create analytics instance and populate with sample data
    analytics = WorkflowAnalytics()
    analytics = create_sample_data(analytics)
    optimizer = WorkflowOptimizer(analytics)

    wf_id = "DataPipeline"
    print(f"Building workflow graph for {wf_id}...")
    graph = optimizer.build_workflow_graph(wf_id)
    print(f"Nodes: {len(graph.nodes)} nodes")
    print(f"Edges: {len(graph.edges)} edges")

    print(f"\nIdentifying critical path for {wf_id}...")
    critical_path = optimizer.identify_critical_path(wf_id)
    print(f"Critical Path: {critical_path}")

    print(f"\nClustering executions for {wf_id}...")
    clustering = optimizer.cluster_executions(wf_id)
    print(
        f"Clustering results: {len(clustering['labels'])} executions clustered into {len(set(clustering['labels']))} clusters"
    )

    print(f"\nGenerating optimization recommendations for {wf_id}...")
    recommendations = optimizer.recommend_optimizations(wf_id)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['type'].title()} (Priority: {rec.get('priority', 'N/A')})")
        print(f"   {rec['description']}")
        if "details" in rec:
            print(f"   Details: {rec['details']}")
        if "steps" in rec:
            print(f"   Steps: {', '.join(rec['steps'])}")

    print(f"\nEvaluating optimization impact for {wf_id} (simulated)...")
    impact = optimizer.evaluate_optimization_impact(wf_id, "simulated_optimization")
    print(f"Before ({impact['before']['time_period']}):")
    print(f"  Success Rate: {impact['before']['success_rate']:.1f}%")
    print(f"  Avg Duration: {impact['before']['avg_duration']:.1f}s")
    print(f"After ({impact['after']['time_period']}):")
    print(f"  Success Rate: {impact['after']['success_rate']:.1f}%")
    print(f"  Avg Duration: {impact['after']['avg_duration']:.1f}s")
    print("Impact:")
    print(f"  Success Rate Change: {impact['impact']['success_rate_change']:.1f}%")
    print(f"  Duration Change: {impact['impact']['duration_change']:.1f}s")
