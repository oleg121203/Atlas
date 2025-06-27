import unittest
from unittest.mock import MagicMock, patch

from workflow_simulation import WorkflowSimulation


class TestWorkflowSimulation(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.simulator = WorkflowSimulation()

    def test_add_scenario(self):
        """Test adding a scenario to the simulation environment."""
        conditions = {"load": "high", "failure_rate": 0.1}
        self.simulator.add_scenario("scenario1", conditions)
        self.assertEqual(len(self.simulator.scenarios), 1)
        self.assertEqual(self.simulator.scenarios[0]["id"], "scenario1")
        self.assertEqual(self.simulator.scenarios[0]["conditions"], conditions)

    def test_run_simulation_success(self):
        """Test running a simulation with a valid scenario."""
        conditions = {"load": "normal"}
        self.simulator.add_scenario("scenario2", conditions)
        mock_workflow = MagicMock()
        mock_workflow.id = "wf_test"

        result = self.simulator.run_simulation(mock_workflow, "scenario2")
        self.assertEqual(result["scenario_id"], "scenario2")
        self.assertEqual(result["workflow_id"], "wf_test")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(self.simulator.results), 1)

    def test_run_simulation_invalid_scenario(self):
        """Test running a simulation with an invalid scenario ID."""
        mock_workflow = MagicMock()
        with self.assertRaises(ValueError):
            self.simulator.run_simulation(mock_workflow, "invalid_scenario")

    @patch("time.time")
    @patch("time.sleep")
    def test_benchmark_workflow(self, mock_sleep, mock_time):
        """Test benchmarking a workflow over multiple iterations."""
        mock_time.side_effect = [
            0.0,
            0.1,
            0.1,
            0.2,
            0.2,
            0.3,
            0.3,
            0.4,
            0.4,
            0.5,
            0.5,
            0.6,
            0.6,
            0.7,
            0.7,
            0.8,
            0.8,
            0.9,
            0.9,
            1.0,
        ]
        mock_sleep.return_value = None
        mock_workflow = MagicMock()
        mock_workflow.id = "wf_bench"

        result = self.simulator.benchmark_workflow(mock_workflow, iterations=10)
        self.assertEqual(result["iterations"], 10)
        self.assertAlmostEqual(result["average_time"], 0.1)
        self.assertIn("wf_bench", self.simulator.benchmarks)

    def test_analyze_results_no_simulations(self):
        """Test analyzing results when no simulations have been run."""
        analysis = self.simulator.analyze_results()
        self.assertEqual(analysis["total_simulations"], 0)
        self.assertEqual(analysis["failure_rate"], 0)
        self.assertEqual(len(analysis["recommendations"]), 0)

    def test_analyze_results_with_simulations(self):
        """Test analyzing results with completed simulations."""
        conditions = {"load": "normal"}
        self.simulator.add_scenario("scenario3", conditions)
        mock_workflow = MagicMock()
        mock_workflow.id = "wf_test_analyze"
        self.simulator.run_simulation(mock_workflow, "scenario3")
        analysis = self.simulator.analyze_results()
        self.assertEqual(analysis["total_simulations"], 1)
        self.assertEqual(analysis["failure_rate"], 0)
        self.assertEqual(len(analysis["recommendations"]), 0)

    def test_get_dashboard_data(self):
        """Test preparing data for the simulation results dashboard."""
        conditions = {"load": "normal"}
        self.simulator.add_scenario("scenario4", conditions)
        mock_workflow = MagicMock()
        mock_workflow.id = "wf_test_dashboard"
        self.simulator.run_simulation(mock_workflow, "scenario4")
        dashboard_data = self.simulator.get_dashboard_data()
        self.assertIn("simulation_results", dashboard_data)
        self.assertIn("benchmarks", dashboard_data)
        self.assertIn("analysis", dashboard_data)
        self.assertEqual(len(dashboard_data["simulation_results"]), 1)


if __name__ == "__main__":
    unittest.main()
