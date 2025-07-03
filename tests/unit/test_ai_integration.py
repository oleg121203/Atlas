import unittest
from unittest.mock import patch

from core.ai_integration import AIModelManager, automate_ai_task, get_ai_suggestion


class TestAIModelManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = AIModelManager()

    def test_initialization(self):
        """Test AIModelManager initialization."""
        manager = AIModelManager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, AIModelManager)
        self.assertTrue(hasattr(manager, "models"))
        self.assertTrue(hasattr(manager, "default_models"))

    def test_register_model(self):
        """Test registering a new model."""
        manager = AIModelManager()
        model_name = "test_model"
        model_info = {"type": "mock", "capabilities": ["test"], "provider": "mock"}
        with patch.object(manager, "save_models", return_value=None):
            manager.set_model(model_name, model_info)
            self.assertIn(model_name, manager.models)
            self.assertEqual(manager.models[model_name], model_info)

    def test_get_model(self):
        """Test retrieving a model."""
        manager = AIModelManager()
        model_name = "test_model"
        model_info = {"type": "mock", "capabilities": ["test"], "provider": "mock"}
        with patch.object(manager, "save_models", return_value=None):
            manager.set_model(model_name, model_info)
            retrieved = manager.get_model(model_name)
            self.assertEqual(retrieved, model_info)

    def test_get_active_model(self):
        """Test getting the active model."""
        model_id = "test-model"
        config = {"provider": "mock", "capabilities": ["general"]}

        # Set a model
        self.manager.set_model(model_id, config)
        retrieved_model = self.manager.get_model(model_id)
        self.assertIsNotNone(retrieved_model)
        self.assertEqual(retrieved_model, config)

    @patch("core.ai_integration.AIModelManager._infer_local")
    def test_infer(self, mock_infer_local):
        """Test infer method with a valid model and input data."""
        mock_infer_local.return_value = "Inference result"
        model_id = "test-model"
        data = {"input": "test input"}

        # Set a model before inference with a supported provider
        config = {"provider": "local", "capabilities": ["general"]}
        self.manager.set_model(model_id, config)
        result = self.manager.infer(model_id, data)

        self.assertEqual(result, mock_infer_local.return_value)
        mock_infer_local.assert_called_once_with(config, data, None)

    def test_get_ai_suggestion(self):
        """Test getting AI suggestion."""
        with patch("core.ai_integration.get_ai_model_manager") as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.get_suggestion.return_value = "suggestion"
            result = get_ai_suggestion("test_model", {"key": "value"}, "general")
            self.assertEqual(result, "suggestion")

    def test_automate_ai_task(self):
        """Test automating AI task."""
        with patch("core.ai_integration.get_ai_model_manager") as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.automate_task.return_value = {"steps": ["step1", "step2"]}
            result = automate_ai_task("test_model", "test task", {"key": "value"})
            self.assertEqual(result, {"steps": ["step1", "step2"]})

    def test_automate_ai_task_invalid_json(self):
        """Test automating AI task with invalid JSON handling."""
        with patch("core.ai_integration.get_ai_model_manager") as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.automate_task.side_effect = ValueError
            with self.assertRaises(ValueError):
                automate_ai_task("test_model", "test task", {"key": "value"})


class TestAIFunctions(unittest.TestCase):
    def test_get_ai_suggestion(self):
        """Test getting AI suggestion."""
        with patch("core.ai_integration.get_ai_model_manager") as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.get_suggestion.return_value = "suggestion"
            result = get_ai_suggestion("test_model", {"key": "value"}, "general")
            self.assertEqual(result, "suggestion")

    def test_automate_ai_task(self):
        """Test automating AI task."""
        with patch("core.ai_integration.get_ai_model_manager") as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.automate_task.return_value = {"steps": ["step1", "step2"]}
            result = automate_ai_task("test_model", "test task", {"key": "value"})
            self.assertEqual(result, {"steps": ["step1", "step2"]})

    def test_automate_ai_task_invalid_json(self):
        """Test automating AI task with invalid JSON handling."""
        with patch("core.ai_integration.get_ai_model_manager") as mock_manager:
            mock_instance = mock_manager.return_value
            mock_instance.automate_task.side_effect = ValueError
            with self.assertRaises(ValueError):
                automate_ai_task("test_model", "test task", {"key": "value"})


if __name__ == "__main__":
    unittest.main()
