import unittest
from unittest.mock import Mock, patch

from core.lazy_loader import LazyLoader


# Test suite for LazyLoader class
class TestLazyLoader(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.loader_module = LazyLoader(module_name="dummy_module", attribute_name="")
        self.loader_attribute = LazyLoader(
            module_name="dummy_module", attribute_name="dummy_attribute"
        )

    def test_initialization(self):
        """Test that the lazy loader initializes correctly."""
        self.assertEqual(self.loader_module.module_name, "dummy_module")
        self.assertEqual(self.loader_attribute.attribute_name, "dummy_attribute")
        self.assertIsNone(self.loader_module._module)
        self.assertIsNone(self.loader_attribute._attribute)

    def test_lazy_loader_init(self):
        module_name = "test_module"
        loader = LazyLoader(module_name, "")
        self.assertEqual(loader.module_name, module_name)
        self.assertIsNone(loader._module)

    def test_lazy_load_module(self):
        module_name = "test_module"
        loader = LazyLoader(module_name, "")
        mock_module = Mock()
        with patch("importlib.import_module", return_value=mock_module) as mock_import:
            print(f"Before get(): loader._module = {loader._module}")
            result = loader.get()
            print(f"After get(): loader._module = {loader._module}, result = {result}")
            if result is None:
                print("get() returned None, checking direct attribute access")
                try:
                    direct_access = loader._module
                    print(f"Direct access to _module: {direct_access}")
                except AttributeError:
                    print("Direct access to _module failed")
            self.assertEqual(
                result,
                mock_module,
                "get() should return the module when attribute_name is empty",
            )
            self.assertEqual(loader._module, mock_module)
            mock_import.assert_called_once_with(module_name)

    def test_lazy_load_attribute(self):
        module_name = "test_module"
        attribute_name = "test_attribute"
        loader = LazyLoader(module_name, attribute_name)
        mock_module = Mock()
        mock_attribute = Mock()
        setattr(mock_module, attribute_name, mock_attribute)
        with patch("importlib.import_module", return_value=mock_module) as mock_import:
            print(
                f"Before get(): loader._module = {loader._module}, loader._attribute = {loader._attribute}"
            )
            result = loader.get()
            print(
                f"After get(): loader._module = {loader._module}, loader._attribute = {loader._attribute}, result = {result}"
            )
            self.assertEqual(result, mock_attribute)
            self.assertEqual(loader._attribute, mock_attribute)
            mock_import.assert_called_once_with(module_name)

    def test_direct_attribute_access(self):
        mock_module = Mock()
        mock_attribute = Mock()
        mock_module.test_attribute = mock_attribute
        with patch("importlib.import_module", return_value=mock_module) as mock_import:
            loader = LazyLoader("test_module", "test_attribute")
            print(
                f"Before access: loader._module = {loader._module}, loader._attribute = {loader._attribute}"
            )
            result = loader.test_attribute
            print(
                f"After access: loader._module = {loader._module}, loader._attribute = {loader._attribute}, result = {result}"
            )
            self.assertEqual(result, mock_attribute)
            mock_import.assert_called_once_with("test_module")

    def test_get_module_without_loading(self):
        module_name = "test_module"
        loader = LazyLoader(module_name, "")
        mock_module = Mock()
        with patch("importlib.import_module", return_value=mock_module) as mock_import:
            print(f"First get(): loader._module = {loader._module}")
            loader.get()
            print(f"After first get(): loader._module = {loader._module}")
            result = loader.get()
            print(f"After second get(): result = {result}")
            self.assertEqual(
                result,
                mock_module,
                "get() should return the module even on second call",
            )
            mock_import.assert_called_once_with(module_name)

    def test_load_module_failure_once(self):
        module_name = "test_module"
        loader = LazyLoader(module_name, "")
        with patch(
            "importlib.import_module", side_effect=ImportError("Module not found")
        ) as mock_import:
            with self.assertRaises(ImportError):
                loader.get()
            mock_import.assert_called_once_with(module_name)

    def test_load_module(self):
        """Test loading a module lazily."""
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_import.return_value = mock_module
            print(f"Before get(): loader_module._module = {self.loader_module._module}")
            result = self.loader_module.get()
            print(
                f"After get(): loader_module._module = {self.loader_module._module}, result = {result}"
            )
            self.assertEqual(
                result,
                mock_module,
                "get() should return the module for empty attribute_name",
            )
            self.assertEqual(self.loader_module._module, mock_module)
            mock_import.assert_called_once_with("dummy_module")

    def test_load_attribute(self):
        """Test loading an attribute lazily."""
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_attribute = Mock()
            mock_module.dummy_attribute = mock_attribute
            mock_import.return_value = mock_module
            print(
                f"Before get(): loader_attribute._module = {self.loader_attribute._module}, loader_attribute._attribute = {self.loader_attribute._attribute}"
            )
            result = self.loader_attribute.get()
            print(
                f"After get(): loader_attribute._module = {self.loader_attribute._module}, loader_attribute._attribute = {self.loader_attribute._attribute}, result = {result}"
            )
            self.assertEqual(result, mock_attribute)
            self.assertEqual(self.loader_attribute._attribute, mock_attribute)
            mock_import.assert_called_once_with("dummy_module")

    def test_load_module_twice(self):
        """Test that loading a module twice doesn't re-import."""
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_import.return_value = mock_module
            print(
                f"Before first get(): loader_module._module = {self.loader_module._module}"
            )
            result1 = self.loader_module.get()
            print(
                f"After first get(): loader_module._module = {self.loader_module._module}, result1 = {result1}"
            )
            result2 = self.loader_module.get()
            print(f"After second get(): result2 = {result2}")
            self.assertEqual(
                result1,
                result2,
                "get() should return the same result on multiple calls",
            )
            mock_import.assert_called_once_with("dummy_module")

    def test_load_module_failure(self):
        """Test that an ImportError is raised if module loading fails."""
        with patch("importlib.import_module", side_effect=ImportError) as mock_import:
            with self.assertRaises(ImportError):
                self.loader_module.get()
            mock_import.assert_called_once_with("dummy_module")


if __name__ == "__main__":
    unittest.main()
