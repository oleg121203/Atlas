"""
Unit tests for SelfHealingManager

Tests the automated diagnosis and self-regeneration mechanisms for Atlas components.
"""

import unittest
import os
import shutil
from unittest.mock import patch, MagicMock

from core.self_healing import SelfHealingManager
from core.logging import get_logger

logger = get_logger("TestSelfHealing")

class TestSelfHealingManager(unittest.TestCase):
    """Test cases for SelfHealingManager."""

    def setUp(self):
        """Set up test environment before each test."""
        self.app_context = {"plugin_registry": MagicMock(), "expected_modules": ["test_module"]}
        self.config_patcher = patch("core.self_healing.get_config")
        self.mock_config = self.config_patcher.start()
        self.mock_config.return_value = {
            "module_backup_dir": "backups/modules",
            "plugin_backup_dir": "backups/plugins",
            "file_backup_dir": "backups/files",
            "config_files": ["configs/test_config.json"],
            "critical_files": ["critical/test_file.txt"],
            "default_config": {"setting": "value"}
        }
        self.self_healing = SelfHealingManager(self.app_context)
        
        # Create temporary directories for testing
        os.makedirs("backups/modules", exist_ok=True)
        os.makedirs("backups/plugins", exist_ok=True)
        os.makedirs("backups/files", exist_ok=True)
        os.makedirs("modules", exist_ok=True)
        os.makedirs("plugins", exist_ok=True)
        os.makedirs("configs", exist_ok=True)
        os.makedirs("critical", exist_ok=True)

    def tearDown(self):
        """Clean up test environment after each test."""
        self.config_patcher.stop()
        # Remove temporary directories
        shutil.rmtree("backups", ignore_errors=True)
        shutil.rmtree("modules", ignore_errors=True)
        shutil.rmtree("plugins", ignore_errors=True)
        shutil.rmtree("configs", ignore_errors=True)
        shutil.rmtree("critical", ignore_errors=True)

    def test_diagnose_system_modules(self):
        """Test diagnosis of system modules."""
        with patch("core.self_healing.importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            results = self.self_healing.diagnose_system()
            self.assertIn("modules", results)
            for module_name, status in results["modules"].items():
                self.assertFalse(status, f"Module {module_name} should fail diagnosis")

    def test_diagnose_system_plugins(self):
        """Test diagnosis of system plugins."""
        self.app_context["plugin_registry"].get_plugin_names.return_value = ["test_plugin"]
        self.app_context["plugin_registry"].get_plugin.return_value = None
        results = self.self_healing.diagnose_system()
        self.assertIn("plugins", results)
        self.assertIn("test_plugin", results["plugins"])
        self.assertFalse(results["plugins"]["test_plugin"], "Plugin should fail diagnosis")

    def test_diagnose_system_configurations(self):
        """Test diagnosis of system configurations."""
        results = self.self_healing.diagnose_system()
        self.assertIn("configurations", results)
        self.assertIn("configs/test_config.json", results["configurations"])
        self.assertFalse(results["configurations"]["configs/test_config.json"], "Configuration file should not exist")

    def test_diagnose_system_files(self):
        """Test diagnosis of critical files."""
        results = self.self_healing.diagnose_system()
        self.assertIn("files", results)
        self.assertIn("critical/test_file.txt", results["files"])
        self.assertFalse(results["files"]["critical/test_file.txt"], "Critical file should not exist")

    def test_regenerate_module_from_backup(self):
        """Test regenerating a module from backup."""
        with open("backups/modules/test_module.py", "w") as f:
            f.write("# Backup module content")
        success = self.self_healing.regenerate_component("module", "test_module")
        self.assertTrue(success, "Module regeneration from backup should succeed")
        self.assertTrue(os.path.exists("modules/test_module.py"), "Module file should be created")

    def test_regenerate_module_no_backup(self):
        """Test regenerating a module without backup (template creation)."""
        success = self.self_healing.regenerate_component("module", "test_module")
        self.assertTrue(success, "Module regeneration with template should succeed")
        self.assertTrue(os.path.exists("modules/test_module.py"), "Module file should be created")
        with open("modules/test_module.py", "r") as f:
            content = f.read()
        self.assertIn("Auto-generated module template", content, "Template content should be in file")

    def test_regenerate_plugin_from_backup(self):
        """Test regenerating a plugin from backup."""
        with open("backups/plugins/test_plugin.py", "w") as f:
            f.write("# Backup plugin content")
        success = self.self_healing.regenerate_component("plugin", "test_plugin")
        self.assertTrue(success, "Plugin regeneration from backup should succeed")
        self.assertTrue(os.path.exists("plugins/test_plugin.py"), "Plugin file should be created")

    def test_regenerate_plugin_no_backup(self):
        """Test regenerating a plugin without backup (template creation)."""
        success = self.self_healing.regenerate_component("plugin", "test_plugin")
        self.assertTrue(success, "Plugin regeneration with template should succeed")
        self.assertTrue(os.path.exists("plugins/test_plugin.py"), "Plugin file should be created")
        with open("plugins/test_plugin.py", "r") as f:
            content = f.read()
        self.assertIn("Auto-generated plugin template", content, "Template content should be in file")

    def test_regenerate_configuration(self):
        """Test regenerating a configuration file."""
        success = self.self_healing.regenerate_component("configuration", "configs/test_config.json")
        self.assertTrue(success, "Configuration regeneration should succeed")
        self.assertTrue(os.path.exists("configs/test_config.json"), "Configuration file should be created")
        with open("configs/test_config.json", "r") as f:
            import json
            content = json.load(f)
        self.assertEqual(content, {"setting": "value"}, "Configuration content should match default")

    def test_regenerate_file_from_backup(self):
        """Test regenerating a critical file from backup."""
        with open("backups/files/test_file.txt", "w") as f:
            f.write("Backup file content")
        success = self.self_healing.regenerate_component("file", "critical/test_file.txt")
        self.assertTrue(success, "File regeneration from backup should succeed")
        self.assertTrue(os.path.exists("critical/test_file.txt"), "File should be created")

    def test_regenerate_file_no_backup(self):
        """Test regenerating a critical file without backup (placeholder creation)."""
        success = self.self_healing.regenerate_component("file", "critical/test_file.txt")
        self.assertTrue(success, "File regeneration with placeholder should succeed")
        self.assertTrue(os.path.exists("critical/test_file.txt"), "File should be created")
        with open("critical/test_file.txt", "r") as f:
            content = f.read()
        self.assertIn("Auto-generated placeholder", content, "Placeholder content should be in file")

    def test_auto_heal(self):
        """Test the auto-heal process."""
        # Setup diagnostic results to simulate issues
        self.self_healing.diagnostic_results = {
            "modules": {"test_module": False},
            "plugins": {"test_plugin": False},
            "configurations": {"configs/test_config.json": False},
            "files": {"critical/test_file.txt": False}
        }
        results = self.self_healing.auto_heal()
        self.assertEqual(len(results), 4, "Auto-heal should attempt to fix all 4 components")
        for component_type, component_name, success in results:
            self.assertTrue(success, f"Healing of {component_type} {component_name} should succeed")

if __name__ == "__main__":
    unittest.main()
