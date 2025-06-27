import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import time

from performance_optimization.optimization_strategies import OptimizationStrategies
from performance_optimization.performance_monitor import PerformanceMonitor


class DashboardSimulator:
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.optimizer = OptimizationStrategies()

    def simulate_dashboard_interaction(
        self, interaction_name: str, min_time: float = 0.01, max_time: float = 0.1
    ) -> float:
        """
        Simulate a dashboard interaction and measure its response time.

        Args:
            interaction_name (str): Name of the interaction to simulate.
            min_time (float): Minimum simulated response time in seconds.
            max_time (float): Maximum simulated response time in seconds.

        Returns:
            float: Simulated response time for the interaction.
        """
        start_time = time.time()
        # Simulate some processing time
        time.sleep(random.uniform(min_time, max_time))
        response_time = time.time() - start_time
        self.monitor.measure_response_time(interaction_name, response_time)
        return response_time

    def run_simulation(self, num_interactions: int = 10) -> dict:
        """
        Run a simulation of multiple dashboard interactions.

        Args:
            num_interactions (int): Number of interactions to simulate.

        Returns:
            dict: Performance report after the simulation.
        """
        self.monitor.start_monitoring()

        interaction_types = [
            "load_dashboard",
            "click_widget",
            "filter_data",
            "expand_chart",
            "refresh_data",
            "switch_tab",
        ]

        for _i in range(num_interactions):
            interaction = random.choice(interaction_types)
            # Vary the simulated response times to mimic real usage
            if interaction == "load_dashboard":
                self.simulate_dashboard_interaction(interaction, 0.2, 0.8)
            elif interaction == "refresh_data":
                self.simulate_dashboard_interaction(interaction, 0.1, 0.5)
            else:
                self.simulate_dashboard_interaction(interaction, 0.05, 0.2)

        metrics = self.monitor.stop_monitoring()
        report = self.monitor.generate_performance_report()
        bottlenecks = self.monitor.identify_bottlenecks(threshold=0.3)
        optimizations = self.monitor.optimize_performance(bottlenecks)
        applied_optimizations = self.optimizer.suggest_optimizations(bottlenecks)

        return {
            "metrics": metrics,
            "report": report,
            "bottlenecks": bottlenecks,
            "optimizations": optimizations,
            "applied_optimizations": applied_optimizations,
        }


if __name__ == "__main__":
    simulator = DashboardSimulator()
    results = simulator.run_simulation(20)
    print("Performance Report:")
    print(results["report"])
    print("\nIdentified Bottlenecks:")
    print(results["bottlenecks"])
    print("\nOptimization Suggestions:")
    print(results["optimizations"])
    print("\nApplied Optimizations:")
    print(results["applied_optimizations"])
