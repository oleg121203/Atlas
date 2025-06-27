import json
import os
import unittest

from workflow.workflow_pattern_library import WorkflowPatternLibrary


class TestWorkflowPatternLibrary(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_library_path = "test_workflow_patterns.json"
        self.library = WorkflowPatternLibrary(library_path=self.test_library_path)
        self.library.marketplace_patterns = {}
        self.library.marketplace_path = "test_marketplace_patterns.json"
        # Clear any existing test files
        if os.path.exists(self.test_library_path):
            os.remove(self.test_library_path)
        if os.path.exists(self.library.marketplace_path):
            os.remove(self.library.marketplace_path)
        # Reset to default patterns
        self.library.initialize_default_patterns()

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_library_path):
            os.remove(self.test_library_path)
        if os.path.exists(self.library.marketplace_path):
            os.remove(self.library.marketplace_path)

    def test_initialization_with_default_patterns(self):
        """Test that library initializes with default patterns."""
        self.assertGreater(len(self.library.patterns), 0)
        self.assertIn("etl_basic", self.library.patterns)
        self.assertIn("ml_training", self.library.patterns)
        self.assertIn("batch_processing", self.library.patterns)
        self.assertGreater(len(self.library.categories), 0)
        self.assertGreater(len(self.library.tags), 0)
        self.assertEqual(len(self.library.marketplace_patterns), 0)

    def test_add_pattern(self):
        """Test adding a new workflow pattern to the library."""
        pattern_id = "test_pattern"
        structure = {
            "steps": [{"id": 1, "name": "Test Step", "type": "test", "config": {}}],
            "connections": [],
        }
        result = self.library.add_pattern(
            pattern_id=pattern_id,
            name="Test Pattern",
            description="A test workflow pattern",
            category="Test Category",
            tags=["test", "experimental"],
            structure=structure,
        )
        self.assertTrue(result)
        self.assertIn(pattern_id, self.library.patterns)
        self.assertIn("Test Category", self.library.categories)
        self.assertIn(pattern_id, self.library.categories["Test Category"])
        self.assertIn("test", self.library.tags)
        self.assertIn(pattern_id, self.library.tags["test"])
        self.assertIn("experimental", self.library.tags)
        self.assertIn(pattern_id, self.library.tags["experimental"])
        pattern = self.library.get_pattern(pattern_id)
        self.assertEqual(pattern["name"], "Test Pattern")
        self.assertEqual(pattern["description"], "A test workflow pattern")
        self.assertEqual(pattern["structure"], structure)

    def test_add_pattern_duplicate_id(self):
        """Test adding a pattern with a duplicate ID fails."""
        result = self.library.add_pattern(
            pattern_id="etl_basic",
            name="Duplicate ETL",
            description="This should fail",
            category="Data Processing",
            tags=["duplicate"],
            structure={},
        )
        self.assertFalse(result)
        pattern = self.library.get_pattern("etl_basic")
        self.assertEqual(pattern["name"], "Basic ETL Pipeline")

    def test_update_pattern(self):
        """Test updating an existing pattern."""
        pattern_id = "etl_basic"
        original_pattern = self.library.get_pattern(pattern_id)
        old_category = original_pattern["category"]
        old_tags = original_pattern["tags"].copy()

        result = self.library.update_pattern(
            pattern_id=pattern_id,
            name="Updated ETL Pipeline",
            description="Updated description",
            category="Updated Category",
            tags=["updated", "modified"],
            version="2.0.0",
        )
        self.assertTrue(result)
        updated_pattern = self.library.get_pattern(pattern_id)
        self.assertEqual(updated_pattern["name"], "Updated ETL Pipeline")
        self.assertEqual(updated_pattern["description"], "Updated description")
        self.assertEqual(updated_pattern["category"], "Updated Category")
        self.assertEqual(updated_pattern["tags"], ["updated", "modified"])
        self.assertEqual(updated_pattern["version"], "2.0.0")
        self.assertIn("Updated Category", self.library.categories)
        self.assertIn(pattern_id, self.library.categories["Updated Category"])
        self.assertNotIn(pattern_id, self.library.categories.get(old_category, []))
        self.assertIn("updated", self.library.tags)
        self.assertIn(pattern_id, self.library.tags["updated"])
        self.assertIn("modified", self.library.tags)
        self.assertIn(pattern_id, self.library.tags["modified"])
        for old_tag in old_tags:
            if old_tag in self.library.tags:
                self.assertNotIn(pattern_id, self.library.tags[old_tag])

    def test_update_nonexistent_pattern(self):
        """Test updating a non-existent pattern fails."""
        result = self.library.update_pattern("nonexistent", name="Should Fail")
        self.assertFalse(result)

    def test_delete_pattern(self):
        """Test deleting a pattern from the library."""
        pattern_id = "etl_basic"
        original_pattern = self.library.get_pattern(pattern_id)
        category = original_pattern["category"]
        tags = original_pattern["tags"].copy()

        result = self.library.delete_pattern(pattern_id)
        self.assertTrue(result)
        self.assertNotIn(pattern_id, self.library.patterns)
        self.assertNotIn(pattern_id, self.library.categories.get(category, []))
        for tag in tags:
            if tag in self.library.tags:
                self.assertNotIn(pattern_id, self.library.tags[tag])

    def test_delete_nonexistent_pattern(self):
        """Test deleting a non-existent pattern fails."""
        result = self.library.delete_pattern("nonexistent")
        self.assertFalse(result)

    def test_get_pattern(self):
        """Test retrieving a specific pattern by ID."""
        pattern = self.library.get_pattern("etl_basic")
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern["name"], "Basic ETL Pipeline")
        self.assertEqual(pattern["category"], "Data Processing")

        pattern = self.library.get_pattern("nonexistent")
        self.assertIsNone(pattern)

    def test_list_patterns(self):
        """Test listing patterns with and without filters."""
        all_patterns = self.library.list_patterns()
        self.assertGreaterEqual(len(all_patterns), 3)
        self.assertTrue(any(p["id"] == "etl_basic" for p in all_patterns))

        data_patterns = self.library.list_patterns(category="Data Processing")
        self.assertGreaterEqual(len(data_patterns), 2)
        self.assertTrue(any(p["id"] == "etl_basic" for p in data_patterns))
        self.assertTrue(any(p["id"] == "batch_processing" for p in data_patterns))

        ml_patterns = self.library.list_patterns(category="Machine Learning")
        self.assertEqual(len(ml_patterns), 1)
        self.assertEqual(ml_patterns[0]["id"], "ml_training")

        etl_patterns = self.library.list_patterns(tag="ETL")
        self.assertEqual(len(etl_patterns), 1)
        self.assertEqual(etl_patterns[0]["id"], "etl_basic")

        data_ml_patterns = self.library.list_patterns(
            category="Data Processing", tag="data"
        )
        self.assertGreaterEqual(len(data_ml_patterns), 2)
        self.assertTrue(any(p["id"] == "etl_basic" for p in data_ml_patterns))
        self.assertTrue(any(p["id"] == "batch_processing" for p in data_ml_patterns))

    def test_list_categories(self):
        """Test listing all available categories."""
        categories = self.library.list_categories()
        self.assertGreaterEqual(len(categories), 2)
        self.assertIn("Data Processing", categories)
        self.assertIn("Machine Learning", categories)

    def test_list_tags(self):
        """Test listing all available tags."""
        tags = self.library.list_tags()
        self.assertGreaterEqual(len(tags), 5)
        self.assertIn("ETL", tags)
        self.assertIn("ML", tags)
        self.assertIn("data", tags)

    def test_instantiate_pattern(self):
        """Test instantiating a workflow from a pattern."""
        custom_config = {
            "steps": [
                {"config": {"source": "custom_db"}},
                {"config": {"rules": "custom_rules"}},
                {"config": {"destination": "custom_target"}},
            ]
        }
        workflow = self.library.instantiate_pattern("etl_basic", custom_config)
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow["name"], "Basic ETL Pipeline")
        self.assertEqual(workflow["based_on_pattern"], "etl_basic")
        self.assertEqual(len(workflow["structure"]["steps"]), 3)
        self.assertEqual(
            workflow["structure"]["steps"][0]["config"]["source"], "custom_db"
        )
        self.assertEqual(
            workflow["structure"]["steps"][1]["config"]["rules"], "custom_rules"
        )
        self.assertEqual(
            workflow["structure"]["steps"][2]["config"]["destination"], "custom_target"
        )

        pattern = self.library.get_pattern("etl_basic")
        self.assertEqual(pattern["usage_count"], 1)

        workflow_no_config = self.library.instantiate_pattern("etl_basic")
        self.assertIsNotNone(workflow_no_config)
        self.assertEqual(workflow_no_config["structure"], pattern["structure"])

        pattern2 = self.library.get_pattern("etl_basic")
        self.assertEqual(pattern2["usage_count"], 2)

    def test_instantiate_nonexistent_pattern(self):
        """Test instantiating a non-existent pattern fails."""
        workflow = self.library.instantiate_pattern("nonexistent")
        self.assertIsNone(workflow)

    def test_search_patterns(self):
        """Test searching patterns by keyword."""
        results = self.library.search_patterns("ETL")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "etl_basic")

        results = self.library.search_patterns("data")
        self.assertGreaterEqual(len(results), 2)
        self.assertTrue(any(p["id"] == "etl_basic" for p in results))
        self.assertTrue(any(p["id"] == "batch_processing" for p in results))

        results = self.library.search_patterns("machine learning")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "ml_training")

        results = self.library.search_patterns("nonexistent")
        self.assertEqual(len(results), 0)

    def test_save_and_load_library(self):
        """Test saving and loading the library from file."""
        # Add a new pattern to ensure we have modified data
        self.library.add_pattern(
            pattern_id="test_save",
            name="Save Test",
            description="Testing save functionality",
            category="Test",
            tags=["save", "test"],
            structure={"steps": [], "connections": []},
        )

        # Save the library
        self.library.save_library()
        self.assertTrue(os.path.exists(self.test_library_path))

        # Read the saved file
        with open(self.test_library_path, "r") as f:
            saved_data = json.load(f)
        self.assertIn("patterns", saved_data)
        self.assertIn("test_save", saved_data["patterns"])
        self.assertIn("categories", saved_data)
        self.assertIn("Test", saved_data["categories"])
        self.assertIn("tags", saved_data)
        self.assertIn("save", saved_data["tags"])

        # Create a new library instance and load the saved data
        new_library = WorkflowPatternLibrary(library_path=self.test_library_path)
        self.assertIn("test_save", new_library.patterns)
        self.assertEqual(new_library.patterns["test_save"]["name"], "Save Test")
        self.assertIn("Test", new_library.categories)
        self.assertIn("test_save", new_library.categories["Test"])
        self.assertIn("save", new_library.tags)
        self.assertIn("test_save", new_library.tags["save"])

    def test_contribute_pattern(self):
        """Test contributing a new pattern to the marketplace."""
        result = self.library.contribute_pattern(
            pattern_id="contrib_test",
            name="Contributed Pattern",
            description="A test contributed pattern",
            category="Test",
            tags=["test", "contrib"],
            structure={"steps": [], "connections": []},
            author="Test Author",
        )
        self.assertTrue(result)
        self.assertIn("contrib_test", self.library.marketplace_patterns)
        pattern = self.library.marketplace_patterns["contrib_test"]
        self.assertEqual(pattern["name"], "Contributed Pattern")
        self.assertEqual(pattern["description"], "A test contributed pattern")
        self.assertEqual(pattern["category"], "Test")
        self.assertEqual(pattern["tags"], ["test", "contrib"])
        self.assertEqual(pattern["author"], "Test Author")
        self.assertEqual(pattern["rating"], 0.0)
        self.assertEqual(pattern["rating_count"], 0)
        self.assertEqual(pattern["usage_count"], 0)
        self.assertEqual(pattern["comments"], [])
        self.assertTrue("created_at" in pattern)
        self.assertTrue("updated_at" in pattern)

    def test_contribute_pattern_duplicate_id(self):
        """Test contributing a pattern with a duplicate ID fails."""
        pattern_id = "contrib_duplicate"
        self.library.contribute_pattern(
            pattern_id=pattern_id,
            name="First",
            description="First Desc",
            category="Test",
            tags=["test"],
            structure={},
            author="Author",
        )
        result = self.library.contribute_pattern(
            pattern_id=pattern_id,
            name="Duplicate Contrib",
            description="This should fail",
            category="Test",
            tags=["duplicate"],
            structure={},
            author="Author",
        )
        self.assertFalse(result)
        pattern = self.library.get_contributed_pattern(pattern_id)
        self.assertEqual(pattern["name"], "First")

    def test_update_contributed_pattern(self):
        """Test updating a contributed pattern."""
        pattern_id = "contrib_update"
        self.library.contribute_pattern(
            pattern_id=pattern_id,
            name="Original",
            description="Original Desc",
            category="Original Cat",
            tags=["orig"],
            structure={},
            author="Author",
        )
        result = self.library.update_contributed_pattern(
            pattern_id=pattern_id,
            name="Updated Contrib",
            description="Updated description",
            category="Updated Category",
            tags=["updated", "modified"],
            version="2.0.0",
        )
        self.assertTrue(result)
        updated_pattern = self.library.get_contributed_pattern(pattern_id)
        self.assertEqual(updated_pattern["name"], "Updated Contrib")
        self.assertEqual(updated_pattern["description"], "Updated description")
        self.assertEqual(updated_pattern["category"], "Updated Category")
        self.assertEqual(updated_pattern["tags"], ["updated", "modified"])
        self.assertEqual(updated_pattern["version"], "2.0.0")

    def test_update_nonexistent_contributed_pattern(self):
        """Test updating a non-existent contributed pattern fails."""
        result = self.library.update_contributed_pattern(
            "nonexistent", name="Should Fail"
        )
        self.assertFalse(result)

    def test_delete_contributed_pattern(self):
        """Test deleting a contributed pattern from the marketplace."""
        pattern_id = "contrib_delete"
        self.library.contribute_pattern(
            pattern_id=pattern_id,
            name="Delete Me",
            description="Delete Desc",
            category="Delete Cat",
            tags=["delete"],
            structure={},
            author="Author",
        )
        result = self.library.delete_contributed_pattern(pattern_id)
        self.assertTrue(result)
        self.assertNotIn(pattern_id, self.library.marketplace_patterns)

    def test_delete_nonexistent_contributed_pattern(self):
        """Test deleting a non-existent contributed pattern fails."""
        result = self.library.delete_contributed_pattern("nonexistent")
        self.assertFalse(result)

    def test_get_contributed_pattern(self):
        """Test retrieving a specific contributed pattern by ID."""
        pattern_id = "contrib_get"
        self.library.contribute_pattern(
            pattern_id=pattern_id,
            name="Get Me",
            description="Get Desc",
            category="Get Cat",
            tags=["get"],
            structure={},
            author="Author",
        )
        pattern = self.library.get_contributed_pattern(pattern_id)
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern["name"], "Get Me")
        self.assertEqual(pattern["category"], "Get Cat")

        pattern = self.library.get_contributed_pattern("nonexistent")
        self.assertIsNone(pattern)

    def test_list_contributed_patterns(self):
        """Test listing contributed patterns with and without filters."""
        # Add some test patterns
        self.library.contribute_pattern(
            "contrib1", "Contrib 1", "Desc 1", "Cat A", ["tag1", "tag2"], {}, "Author 1"
        )
        self.library.contribute_pattern(
            "contrib2", "Contrib 2", "Desc 2", "Cat A", ["tag2", "tag3"], {}, "Author 2"
        )
        self.library.contribute_pattern(
            "contrib3", "Contrib 3", "Desc 3", "Cat B", ["tag3"], {}, "Author 1"
        )

        all_patterns = self.library.list_contributed_patterns()
        self.assertEqual(len(all_patterns), 3)
        self.assertTrue(any(p["id"] == "contrib1" for p in all_patterns))

        cat_a_patterns = self.library.list_contributed_patterns(category="Cat A")
        self.assertEqual(len(cat_a_patterns), 2)
        self.assertTrue(any(p["id"] == "contrib1" for p in cat_a_patterns))
        self.assertTrue(any(p["id"] == "contrib2" for p in cat_a_patterns))

        tag3_patterns = self.library.list_contributed_patterns(tag="tag3")
        self.assertEqual(len(tag3_patterns), 2)
        self.assertTrue(any(p["id"] == "contrib2" for p in tag3_patterns))
        self.assertTrue(any(p["id"] == "contrib3" for p in tag3_patterns))

        author1_patterns = self.library.list_contributed_patterns(author="Author 1")
        self.assertEqual(len(author1_patterns), 2)
        self.assertTrue(any(p["id"] == "contrib1" for p in author1_patterns))
        self.assertTrue(any(p["id"] == "contrib3" for p in author1_patterns))

        filtered_patterns = self.library.list_contributed_patterns(
            category="Cat A", tag="tag2", author="Author 2"
        )
        self.assertEqual(len(filtered_patterns), 1)
        self.assertEqual(filtered_patterns[0]["id"], "contrib2")

    def test_search_contributed_patterns(self):
        """Test searching contributed patterns by keyword."""
        self.library.contribute_pattern(
            "contrib_search1",
            "Search ETL",
            "ETL workflow",
            "Data",
            ["ETL"],
            {},
            "Author",
        )
        self.library.contribute_pattern(
            "contrib_search2",
            "Search Data",
            "Data workflow",
            "Data",
            ["data"],
            {},
            "Searcher",
        )
        self.library.contribute_pattern(
            "contrib_search3", "Other", "Other desc", "Other", ["other"], {}, "Author"
        )

        results = self.library.search_contributed_patterns("ETL")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "contrib_search1")

        results = self.library.search_contributed_patterns("data")
        self.assertEqual(len(results), 2)
        self.assertTrue(any(p["id"] == "contrib_search1" for p in results))
        self.assertTrue(any(p["id"] == "contrib_search2" for p in results))

        results = self.library.search_contributed_patterns("searcher")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "contrib_search2")

        results = self.library.search_contributed_patterns("nonexistent")
        self.assertEqual(len(results), 0)

    def test_instantiate_contributed_pattern(self):
        """Test instantiating a workflow from a contributed pattern."""
        self.library.contribute_pattern(
            "contrib_instantiate",
            "Instantiable",
            "Instantiable pattern",
            "Test",
            ["test"],
            {
                "steps": [{"id": 1, "name": "Test Step", "type": "task", "config": {}}],
                "connections": [],
            },
            "Author",
        )
        workflow = self.library.instantiate_contributed_pattern("contrib_instantiate")
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow["name"], "Instantiable")
        pattern = self.library.get_contributed_pattern("contrib_instantiate")
        self.assertEqual(pattern["usage_count"], 1)

        custom_config = {"steps": [{"config": {"custom": True}}]}
        custom_workflow = self.library.instantiate_contributed_pattern(
            "contrib_instantiate", custom_config=custom_config
        )
        self.assertIsNotNone(custom_workflow)
        self.assertEqual(custom_workflow["name"], "Instantiable")
        self.assertTrue(custom_workflow["structure"]["steps"][0]["config"]["custom"])
        pattern = self.library.get_contributed_pattern("contrib_instantiate")
        self.assertEqual(pattern["usage_count"], 2)

    def test_instantiate_nonexistent_contributed_pattern(self):
        """Test instantiating a non-existent contributed pattern fails."""
        workflow = self.library.instantiate_contributed_pattern("nonexistent")
        self.assertIsNone(workflow)

    def test_rate_contributed_pattern(self):
        """Test rating a contributed pattern."""
        self.library.contribute_pattern(
            "contrib_rate",
            "Rate Me",
            "Rate this pattern",
            "Test",
            ["test"],
            {},
            "Author",
        )
        result = self.library.rate_contributed_pattern("contrib_rate", 4.5)
        self.assertTrue(result)
        pattern = self.library.get_contributed_pattern("contrib_rate")
        self.assertEqual(pattern["rating"], 4.5)
        self.assertEqual(pattern["rating_count"], 1)

        self.library.rate_contributed_pattern("contrib_rate", 3.5)
        pattern = self.library.get_contributed_pattern("contrib_rate")
        self.assertAlmostEqual(pattern["rating"], 4.0)
        self.assertEqual(pattern["rating_count"], 2)

    def test_rate_nonexistent_contributed_pattern(self):
        """Test rating a non-existent contributed pattern fails."""
        result = self.library.rate_contributed_pattern("nonexistent", 5.0)
        self.assertFalse(result)

    def test_comment_on_contributed_pattern(self):
        """Test commenting on a contributed pattern."""
        self.library.contribute_pattern(
            "contrib_comment",
            "Comment Me",
            "Comment on this pattern",
            "Test",
            ["test"],
            {},
            "Author",
        )
        result = self.library.comment_on_contributed_pattern(
            "contrib_comment", "Test User", "This is a great pattern!"
        )
        self.assertTrue(result)
        pattern = self.library.get_contributed_pattern("contrib_comment")
        self.assertEqual(len(pattern["comments"]), 1)
        comment = pattern["comments"][0]
        self.assertEqual(comment["author"], "Test User")
        self.assertEqual(comment["text"], "This is a great pattern!")
        self.assertTrue("timestamp" in comment)

    def test_comment_on_nonexistent_contributed_pattern(self):
        """Test commenting on a non-existent contributed pattern fails."""
        result = self.library.comment_on_contributed_pattern(
            "nonexistent", "Should fail", "Commenter"
        )
        self.assertFalse(result)

    def test_save_and_load_marketplace(self):
        """Test saving and loading the marketplace from file."""
        # Add a contributed pattern to ensure we have modified data
        pattern_id = "contrib_save"
        self.library.contribute_pattern(
            pattern_id=pattern_id,
            name="Marketplace Save Test",
            description="Testing marketplace save functionality",
            category="Marketplace Test",
            tags=["marketplace", "save", "test"],
            structure={"steps": [], "connections": []},
            author="Save Tester",
        )

        # Save the marketplace
        self.library.save_marketplace()
        self.assertTrue(os.path.exists(self.library.marketplace_path))

        # Read the saved file
        with open(self.library.marketplace_path, "r") as f:
            saved_data = json.load(f)
        self.assertIn("patterns", saved_data)
        self.assertIn(pattern_id, saved_data["patterns"])
        self.assertEqual(
            saved_data["patterns"][pattern_id]["name"], "Marketplace Save Test"
        )
        self.assertEqual(saved_data["patterns"][pattern_id]["author"], "Save Tester")

        # Create a new library instance and load the saved marketplace data
        new_library = WorkflowPatternLibrary(library_path=self.test_library_path)
        new_library.marketplace_path = self.library.marketplace_path
        new_library.load_marketplace()
        self.assertIn(pattern_id, new_library.marketplace_patterns)
        saved_pattern = new_library.get_contributed_pattern(pattern_id)
        self.assertEqual(saved_pattern["name"], "Marketplace Save Test")
        self.assertEqual(saved_pattern["author"], "Save Tester")
        self.assertEqual(saved_pattern["category"], "Marketplace Test")
        self.assertEqual(saved_pattern["tags"], ["marketplace", "save", "test"])

    def test_customize_pattern(self):
        """Test customizing an existing pattern with modifications."""
        pattern_id = "etl_basic"
        customizations = {"steps": [{"config": {"source": "custom_source"}}]}

        # Customize without saving as new
        result = self.library.customize_pattern(
            pattern_id, customizations, save_as_new=False
        )
        self.assertIsNone(result)
        modified_pattern = self.library.get_pattern(pattern_id)
        self.assertEqual(
            modified_pattern["structure"]["steps"][0]["config"]["source"],
            "custom_source",
        )
        self.assertTrue("customized" in modified_pattern["tags"])
        self.assertTrue("(Customized)" in modified_pattern["description"])

        # Customize and save as new
        new_id = "custom_etl_test"
        new_result = self.library.customize_pattern(
            pattern_id, customizations, save_as_new=True, new_pattern_id=new_id
        )
        self.assertEqual(new_result, new_id)
        self.assertIn(new_id, self.library.patterns)
        new_pattern = self.library.get_pattern(new_id)
        self.assertEqual(new_pattern["name"], f"Customized {modified_pattern['name']}")
        self.assertEqual(
            new_pattern["structure"]["steps"][0]["config"]["source"], "custom_source"
        )
        self.assertTrue("custom" in new_pattern["tags"])
        self.assertEqual(
            new_pattern["category"], f"Custom {modified_pattern['category']}"
        )

        # Test error on non-existent pattern
        with self.assertRaises(KeyError):
            self.library.customize_pattern("non_existent", customizations)

        # Test error on duplicate new ID
        with self.assertRaises(ValueError):
            self.library.customize_pattern(
                pattern_id, customizations, save_as_new=True, new_pattern_id=new_id
            )

    def test_share_pattern(self):
        """Test sharing/exporting a pattern to a file."""
        pattern_id = "etl_basic"
        destination = "test_export_pattern.json"
        if os.path.exists(destination):
            os.remove(destination)

        result = self.library.share_pattern(pattern_id, destination, format="json")
        self.assertTrue(result)
        self.assertTrue(os.path.exists(destination))
        with open(destination, "r") as f:
            exported_data = json.load(f)
        self.assertEqual(exported_data["id"], pattern_id)
        self.assertEqual(
            exported_data["name"], self.library.get_pattern(pattern_id)["name"]
        )

        # Test YAML format
        yaml_destination = "test_export_pattern.yaml"
        if os.path.exists(yaml_destination):
            os.remove(yaml_destination)
        result_yaml = self.library.share_pattern(
            pattern_id, yaml_destination, format="yaml"
        )
        self.assertTrue(result_yaml)
        self.assertTrue(os.path.exists(yaml_destination))

        # Test error on non-existent pattern
        with self.assertRaises(KeyError):
            self.library.share_pattern("non_existent", destination)

        # Clean up
        if os.path.exists(destination):
            os.remove(destination)
        if os.path.exists(yaml_destination):
            os.remove(yaml_destination)

    def test_import_shared_pattern(self):
        """Test importing a shared pattern from a file."""
        # First, export a pattern to use for import
        pattern_id = "etl_basic"
        export_file = "test_export_pattern.json"
        self.library.share_pattern(pattern_id, export_file, format="json")

        # Import with a new ID
        new_id = "imported_etl_test"
        imported_id = self.library.import_shared_pattern(
            export_file, format="json", pattern_id=new_id
        )
        self.assertEqual(imported_id, new_id)
        self.assertIn(new_id, self.library.patterns)
        imported_pattern = self.library.get_pattern(new_id)
        original_pattern = self.library.get_pattern(pattern_id)
        self.assertEqual(imported_pattern["name"], original_pattern["name"])
        self.assertEqual(imported_pattern["structure"], original_pattern["structure"])
        self.assertTrue("imported" in imported_pattern["tags"])
        self.assertEqual(imported_pattern["category"], "Imported")

        # Test error on duplicate ID
        with self.assertRaises(ValueError):
            self.library.import_shared_pattern(
                export_file, format="json", pattern_id=new_id
            )

        # Test YAML import
        yaml_file = "test_export_pattern.yaml"
        self.library.share_pattern(pattern_id, yaml_file, format="yaml")
        yaml_import_id = "imported_etl_yaml"
        imported_yaml_id = self.library.import_shared_pattern(
            yaml_file, format="yaml", pattern_id=yaml_import_id
        )
        self.assertEqual(imported_yaml_id, yaml_import_id)
        self.assertIn(yaml_import_id, self.library.patterns)

        # Clean up
        if os.path.exists(export_file):
            os.remove(export_file)
        if os.path.exists(yaml_file):
            os.remove(yaml_file)

    def test_validate_pattern_structure(self):
        """Test validating the structure of a workflow pattern."""
        # Valid structure
        valid_structure = {
            "steps": [
                {"id": 1, "name": "Step 1", "type": "task", "config": {}},
                {"id": 2, "name": "Step 2", "type": "task", "config": {}},
            ],
            "connections": [{"from": 1, "to": 2}],
        }
        is_valid, errors = self.library.validate_pattern_structure(valid_structure)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid structure - not a dictionary
        invalid_structure = ["not", "a", "dict"]
        is_valid, errors = self.library.validate_pattern_structure(invalid_structure)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("must be a dictionary", errors[0])

        # Invalid structure - missing steps
        invalid_structure = {"connections": []}
        is_valid, errors = self.library.validate_pattern_structure(invalid_structure)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("must contain a 'steps' list", errors[0])

        # Invalid structure - missing connections
        invalid_structure = {"steps": []}
        is_valid, errors = self.library.validate_pattern_structure(invalid_structure)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("must contain a 'connections' list", errors[0])

        # Invalid structure - step missing required fields
        invalid_structure = {
            "steps": [
                {"id": 1, "type": "task", "config": {}},  # Missing name
                {"id": 2, "name": "Step 2", "config": {}},  # Missing type
                {"id": 3, "name": "Step 3", "type": "task"},  # Missing config
            ],
            "connections": [],
        }
        is_valid, errors = self.library.validate_pattern_structure(invalid_structure)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)
        self.assertTrue(any("must have a valid 'name' field" in e for e in errors))
        self.assertTrue(any("must have a valid 'type' field" in e for e in errors))
        self.assertTrue(
            any("must have a valid 'config' dictionary" in e for e in errors)
        )

        # Invalid structure - connection with invalid step IDs
        invalid_structure = {
            "steps": [{"id": 1, "name": "Step 1", "type": "task", "config": {}}],
            "connections": [
                {"from": 1, "to": 999}  # Invalid 'to' ID
            ],
        }
        is_valid, errors = self.library.validate_pattern_structure(invalid_structure)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("has invalid 'to' field", errors[0])

    def test_validate_pattern(self):
        """Test validating a pattern in the library or marketplace."""
        # Test with existing library pattern
        is_valid, errors = self.library.validate_pattern("etl_basic")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Test with non-existent pattern
        is_valid, errors = self.library.validate_pattern("non_existent")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("not found in library or marketplace", errors[0])

        # Test with contributed pattern
        self.library.contribute_pattern(
            "contrib_valid",
            "Valid Contrib",
            "Valid contributed pattern",
            "Test",
            ["test"],
            {
                "steps": [{"id": 1, "name": "Step", "type": "task", "config": {}}],
                "connections": [],
            },
            "Author",
        )
        is_valid, errors = self.library.validate_pattern("contrib_valid")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_test_pattern_execution(self):
        """Test the execution simulation of a pattern with test config and data."""
        # Test with valid pattern and no test data
        result = self.library.test_pattern_execution("etl_basic")
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["execution_log"]), 0)
        self.assertEqual(len(result["errors"]), 0)
        self.assertIn("Instantiated workflow", result["execution_log"][0])

        # Test with test config
        test_config = {"steps": [{"config": {"source": "test_source"}}]}
        result = self.library.test_pattern_execution(
            "etl_basic", test_config=test_config
        )
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["execution_log"]), 0)
        self.assertEqual(len(result["errors"]), 0)

        # Test with test data
        test_data = [{"input": "test1"}, {"input": "test2"}]
        result = self.library.test_pattern_execution("etl_basic", test_data=test_data)
        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["execution_log"]), 0)
        self.assertEqual(len(result["errors"]), 0)
        self.assertTrue(
            any("Processing test data item 1" in log for log in result["execution_log"])
        )
        self.assertTrue(
            any("Processing test data item 2" in log for log in result["execution_log"])
        )
        self.assertTrue(
            any("Executing Extract" in log for log in result["execution_log"])
        )

        # Test with non-existent pattern
        with self.assertRaises(KeyError):
            self.library.test_pattern_execution("non_existent")


if __name__ == "__main__":
    unittest.main()
