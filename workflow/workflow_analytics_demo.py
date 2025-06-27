"""
Demo script for WorkflowAnalytics class

This script demonstrates the usage of WorkflowAnalytics with sample workflow execution data.
"""

import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from workflow_analytics import WorkflowAnalytics

# Set random seed for reproducibility
random.seed(42)


# Initialize analytics tracker
def create_sample_data(analytics, num_days=7, workflows=None, executions_per_day=5):
    """
    Create sample workflow execution data for demonstration purposes.
    """
    if workflows is None:
        workflows = ["DataPipeline", "MLTraining", "ReportGeneration"]

    now = datetime.now()
    for day in range(num_days):
        date = now - timedelta(days=day)
        for wf in workflows:
            for exec_num in range(executions_per_day):
                start_time = date.replace(
                    hour=random.randint(8, 20), minute=random.randint(0, 59), second=0
                ) - timedelta(minutes=random.randint(30, 120))

                # Random duration between 2 and 30 minutes
                total_duration = random.randint(120, 1800)
                end_time = start_time + timedelta(seconds=total_duration)

                # Success rate: 80% chance of success
                success = random.random() < 0.8
                error_msg = (
                    ""
                    if success
                    else random.choice(
                        ["TimeoutError", "DataValidationError", "ResourceLimitExceeded"]
                    )
                )

                # Create steps (3-6 steps per workflow)
                num_steps = random.randint(3, 6)
                step_duration = total_duration / num_steps
                steps = []
                step_start = start_time
                for i in range(num_steps):
                    step_end = step_start + timedelta(
                        seconds=step_duration + random.randint(-30, 30)
                    )
                    step_success = success or (
                        random.random() < 0.9
                    )  # Steps can succeed even if overall fails
                    steps.append(
                        {
                            "step_id": f"step_{i + 1}",
                            "step_name": f"{wf}_Step{i + 1}",
                            "start_time": step_start,
                            "end_time": step_end,
                            "success": step_success,
                            "error_message": "" if step_success else "Step failed",
                        }
                    )
                    step_start = step_end

                # Record the execution
                analytics.record_execution(
                    workflow_id=wf,
                    execution_id=f"{wf}_{day}_{exec_num}",
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    error_message=error_msg,
                    steps=steps,
                )

    print(
        f"Created sample data for {len(workflows)} workflows over {num_days} days with {executions_per_day} executions per day."
    )
    return analytics


if __name__ == "__main__":
    # Create analytics instance and populate with sample data
    analytics = WorkflowAnalytics()
    analytics = create_sample_data(analytics)

    # Display performance metrics for all workflows
    print("\nOverall Performance Metrics:")
    metrics = analytics.get_performance_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")

    # Display metrics for a specific workflow
    wf_id = "DataPipeline"
    print(f"\nPerformance Metrics for {wf_id}:")
    wf_metrics = analytics.get_performance_metrics(workflow_id=wf_id)
    for key, value in wf_metrics.items():
        print(f"{key}: {value}")

    # Visualize bottlenecks for a specific workflow
    print(f"\nGenerating bottleneck heatmap for {wf_id}...")
    analytics.visualize_bottlenecks_heatmap(workflow_id=wf_id)

    # Show customizable dashboard
    print("\nGenerating customizable dashboard...")
    analytics.customizable_dashboard(
        workflow_ids=["DataPipeline", "MLTraining", "ReportGeneration"], export=True
    )

    # Perform comparative analytics
    print("\nComparative Analytics across Workflows:")
    comparison = analytics.comparative_analytics()
    print(comparison)

    # Train predictive model and make a sample prediction
    print("\nTraining predictive model for failure detection...")
    analytics.train_predictive_model()

    print("\nMaking sample failure prediction...")
    execution_time = datetime.now()
    prediction = analytics.predict_workflow_failure(
        workflow_id="DataPipeline",
        current_duration=600.0,  # 10 minutes
        execution_time=execution_time,
    )
    print(f"Prediction results: {prediction}")

    # Keep plots open until user closes them
    plt.show()
