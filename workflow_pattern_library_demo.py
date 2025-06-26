from workflow_pattern_library import WorkflowPatternLibrary
import json
import os
from datetime import datetime

# Initialize the WorkflowPatternLibrary instance
def run_demo():
    """Run a demonstration of the Workflow Pattern Library functionality."""
    print("=== Workflow Pattern Library Demo ===")
    library = WorkflowPatternLibrary()
    
    # List all available patterns
    print("\n1. Listing all available patterns:")
    patterns = library.list_patterns()
    for pattern in patterns:
        print(f"- {pattern['name']} (ID: {pattern['id']}, Category: {pattern['category']})")
    
    # List all categories
    print("\n2. Listing all categories:")
    categories = library.list_categories()
    print(f"Available categories: {', '.join(categories)}")
    
    # List all tags
    print("\n3. Listing all tags:")
    tags = library.list_tags()
    print(f"Available tags: {', '.join(tags)}")
    
    # Filter patterns by category
    print("\n4. Filtering patterns by category 'Data':")
    data_patterns = library.list_patterns(category="Data")
    for pattern in data_patterns:
        print(f"- {pattern['name']} (ID: {pattern['id']})")
    
    # Filter patterns by tag
    print("\n5. Filtering patterns by tag 'machine_learning':")
    ml_patterns = library.list_patterns(tag="machine_learning")
    for pattern in ml_patterns:
        print(f"- {pattern['name']} (ID: {pattern['id']})")
    
    # Search for patterns
    print("\n6. Searching for patterns with 'training':")
    search_results = library.search_patterns("training")
    for pattern in search_results:
        print(f"- {pattern['name']} (ID: {pattern['id']})")
    
    # View details of a specific pattern
    print("\n7. Viewing details of 'ml_training' pattern:")
    ml_pattern = library.get_pattern("ml_training")
    if ml_pattern:
        print(f"Name: {ml_pattern['name']}")
        print(f"Description: {ml_pattern['description']}")
        print(f"Category: {ml_pattern['category']}")
        print(f"Tags: {', '.join(ml_pattern['tags'])}")
        print(f"Structure: {json.dumps(ml_pattern['structure'], indent=2)[:200]}...")
    
    # Instantiate a pattern without customization
    print("\n8. Instantiating 'etl_basic' pattern without customization:")
    etl_workflow = library.instantiate_pattern("etl_basic")
    if etl_workflow:
        print(f"Instantiated workflow name: {etl_workflow['name']}")
        print(f"Structure: {json.dumps(etl_workflow['structure'], indent=2)[:200]}...")
    
    # Instantiate a pattern with custom configuration
    print("\n9. Instantiating 'ml_training' pattern with custom configuration:")
    custom_config = {
        "steps": [
            {"config": {"data_source": "custom_dataset.csv"}},
            {"config": {"model_type": "custom_model"}}
        ]
    }
    custom_ml_workflow = library.instantiate_pattern("ml_training", custom_config)
    if custom_ml_workflow:
        print(f"Instantiated workflow name: {custom_ml_workflow['name']}")
        print(f"Custom structure: {json.dumps(custom_ml_workflow['structure'], indent=2)[:200]}...")
    
    # Add a new custom pattern
    print("\n10. Adding a new custom workflow pattern:")
    custom_pattern_id = "custom_workflow_1"
    result = library.add_pattern(
        pattern_id=custom_pattern_id,
        name="Custom Workflow",
        description="A custom workflow for specific processing needs",
        category="Custom",
        tags=["custom", "specialized"],
        structure={
            "steps": [
                {"id": 1, "name": "Custom Input", "type": "input", "config": {}},
                {"id": 2, "name": "Custom Process", "type": "process", "config": {}},
                {"id": 3, "name": "Custom Output", "type": "output", "config": {}}
            ],
            "connections": [
                {"from": 1, "to": 2},
                {"from": 2, "to": 3}
            ]
        }
    )
    print(f"Custom pattern added: {result}")
    custom_pattern = library.get_pattern(custom_pattern_id)
    if custom_pattern:
        print(f"Added pattern name: {custom_pattern['name']}")
    
    # Update the custom pattern
    print("\n11. Updating the custom workflow pattern:")
    result = library.update_pattern(
        pattern_id=custom_pattern_id,
        name="Updated Custom Workflow",
        description="An updated custom workflow with enhanced features"
    )
    print(f"Custom pattern updated: {result}")
    updated_pattern = library.get_pattern(custom_pattern_id)
    if updated_pattern:
        print(f"Updated pattern name: {updated_pattern['name']}")
        print(f"Updated description: {updated_pattern['description']}")
    
    # Contribute a pattern to the marketplace
    print("\n12. Contributing a pattern to the marketplace:")
    contrib_pattern_id = "contrib_demo_1"
    contrib_structure = {
        "steps": [
            {"id": 1, "name": "Demo Input", "type": "input", "config": {"source": "demo_data"}},
            {"id": 2, "name": "Demo Process", "type": "process", "config": {"rules": "demo_rules"}}
        ],
        "connections": [
            {"from": 1, "to": 2}
        ]
    }
    result = library.contribute_pattern(
        pattern_id=contrib_pattern_id,
        name="Demo Contributed Pattern",
        description="A demo pattern contributed to the marketplace",
        category="Demo",
        tags=["demo", "contrib"],
        structure=contrib_structure,
        author="Demo Author",
        license="MIT"
    )
    print(f"Pattern contributed to marketplace: {result}")
    contrib_pattern = library.get_contributed_pattern(contrib_pattern_id)
    if contrib_pattern:
        print(f"Contributed pattern name: {contrib_pattern['name']}")
        print(f"Author: {contrib_pattern['author']}")
    
    # List contributed patterns
    print("\n13. Listing contributed patterns in the marketplace:")
    contrib_patterns = library.list_contributed_patterns()
    for pattern in contrib_patterns:
        print(f"- {pattern['name']} (ID: {pattern['id']}, Author: {pattern['author']}, Rating: {pattern.get('rating', 'N/A')})")
    
    # Filter contributed patterns by category
    print("\n14. Filtering contributed patterns by category 'Demo':")
    demo_contrib_patterns = library.list_contributed_patterns(category="Demo")
    for pattern in demo_contrib_patterns:
        print(f"- {pattern['name']} (ID: {pattern['id']})")
    
    # Search contributed patterns
    print("\n15. Searching contributed patterns for 'demo':")
    search_contrib_results = library.search_contributed_patterns("demo")
    for pattern in search_contrib_results:
        print(f"- {pattern['name']} (ID: {pattern['id']})")
    
    # Rate a contributed pattern
    print("\n16. Rating a contributed pattern:")
    result = library.rate_contributed_pattern(contrib_pattern_id, 4.5)
    print(f"Rating recorded: {result}")
    updated_contrib = library.get_contributed_pattern(contrib_pattern_id)
    if updated_contrib:
        print(f"New rating: {updated_contrib.get('rating', 'N/A')} (based on {updated_contrib.get('rating_count', 0)} ratings)")
    
    # Comment on a contributed pattern
    print("\n17. Commenting on a contributed pattern:")
    result = library.comment_on_contributed_pattern(contrib_pattern_id, "This pattern is very useful!", "Demo User")
    print(f"Comment added: {result}")
    updated_contrib = library.get_contributed_pattern(contrib_pattern_id)
    if updated_contrib and updated_contrib.get('comments'):
        for comment in updated_contrib['comments']:
            print(f"- Comment by {comment['author']}: {comment['text']}")
    
    # Instantiate a contributed pattern with customization
    print("\n18. Instantiating a contributed pattern with custom configuration:")
    custom_contrib_config = {
        "steps": [
            {"config": {"source": "custom_demo_data"}},
            {"config": {"rules": "custom_demo_rules"}}
        ]
    }
    contrib_workflow = library.instantiate_contributed_pattern(contrib_pattern_id, custom_contrib_config)
    if contrib_workflow:
        print(f"Instantiated contributed workflow name: {contrib_workflow['name']}")
        print(f"Based on pattern: {contrib_workflow['based_on_pattern']}")
        print(f"Custom structure: {json.dumps(contrib_workflow['structure'], indent=2)[:200]}...")
    
    print("\n19. Customizing a pattern without saving as new:")
    customizations = {"steps": [{"config": {"source": "demo_custom_source"}}]}
    result = library.customize_pattern("etl_basic", customizations, save_as_new=False)
    print(f"Customization applied (saved as new: {result is not None}): {result}")
    modified_pattern = library.get_pattern("etl_basic")
    print(f"Modified pattern description: {modified_pattern['description']}")
    print(f"Modified pattern tags: {modified_pattern['tags']}")
    print(f"Modified structure source: {modified_pattern['structure']['steps'][0]['config']['source']}")

    print("\n20. Customizing a pattern and saving as new:")
    new_custom_id = "demo_custom_etl_2"
    if new_custom_id in library.patterns:
        print(f"Pattern ID {new_custom_id} already exists, using existing pattern.")
    else:
        new_result = library.customize_pattern("etl_basic", customizations, save_as_new=True, new_pattern_id=new_custom_id)
        print(f"New customized pattern created: {new_result}")
        if isinstance(new_result, str):
            new_pattern = library.get_pattern(new_result)
            print(f"New pattern name: {new_pattern['name']}")
            print(f"New pattern category: {new_pattern['category']}")
            print(f"New pattern tags: {new_pattern['tags']}")
        else:
            print(f"Unexpected result format: {type(new_result)}")

    print("\n21. Sharing a pattern to a file:")
    share_destination = "demo_shared_pattern.json"
    share_result = library.share_pattern("etl_basic", share_destination, format="json")
    print(f"Pattern shared to file: {share_result}")
    if share_result and os.path.exists(share_destination):
        with open(share_destination, 'r') as f:
            shared_data = json.load(f)
        print(f"Shared pattern name: {shared_data['name']}")
        os.remove(share_destination)

    print("\n22. Importing a shared pattern from a file:")
    # First create a file to import
    temp_export_file = "temp_export_for_import.json"
    library.share_pattern("ml_training", temp_export_file, format="json")
    import_id = "demo_imported_ml_2"
    try:
        if import_id in library.patterns:
            print(f"Pattern ID {import_id} already exists, skipping import.")
            imported_pattern = library.get_pattern(import_id)
            print(f"Using existing pattern name: {imported_pattern['name']}")
            print(f"Using existing pattern category: {imported_pattern['category']}")
            print(f"Using existing pattern tags: {imported_pattern['tags']}")
        else:
            imported_id = library.import_shared_pattern(temp_export_file, format="json", pattern_id=import_id)
            print(f"Pattern imported with ID: {imported_id}")
            imported_pattern = library.get_pattern(imported_id)
            print(f"Imported pattern name: {imported_pattern['name']}")
            print(f"Imported pattern category: {imported_pattern['category']}")
            print(f"Imported pattern tags: {imported_pattern['tags']}")
    except Exception as e:
        print(f"Error during import: {e}")
    if os.path.exists(temp_export_file):
        os.remove(temp_export_file)

    print("\n23. Validating a pattern structure:")
    is_valid, errors = library.validate_pattern("etl_basic")
    print(f"Pattern 'etl_basic' is valid: {is_valid}")
    if not is_valid:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("No validation errors found.")

    print("\n24. Testing pattern execution without test data:")
    test_result = library.test_pattern_execution("etl_basic")
    print(f"Test status: {test_result['status']}")
    if test_result['status'] == 'success':
        print("Execution log (first few lines):")
        for log_line in test_result['execution_log'][:3]:
            print(f"  - {log_line}")
        if len(test_result['execution_log']) > 3:
            print(f"  ... and {len(test_result['execution_log']) - 3} more lines")
    else:
        print(f"Test failed reason: {test_result.get('reason', 'unknown')}")
        if 'errors' in test_result and test_result['errors']:
            print("Errors:")
            for error in test_result['errors']:
                print(f"  - {error}")

    print("\n25. Testing pattern execution with test data:")
    test_data = [
        {"input": "demo_data_1"},
        {"input": "demo_data_2"}
    ]
    test_data_result = library.test_pattern_execution("etl_basic", test_data=test_data)
    print(f"Test status with data: {test_data_result['status']}")
    if test_data_result['status'] == 'success':
        print("Execution log (first few lines):")
        for log_line in test_data_result['execution_log'][:5]:
            print(f"  - {log_line}")
        if len(test_data_result['execution_log']) > 5:
            print(f"  ... and {len(test_data_result['execution_log']) - 5} more lines")
    else:
        print(f"Test failed reason: {test_data_result.get('reason', 'unknown')}")
        if 'errors' in test_data_result and test_data_result['errors']:
            print("Errors:")
            for error in test_data_result['errors']:
                print(f"  - {error}")

    print("\n26. Version Control Demo:")
    demo_version_control(library)

    print("\n=== End of Workflow Pattern Library Demo ===")

def demo_version_control(library):
    """Demonstrate version control features for workflow patterns."""
    print("\n=== Version Control Demo ===")
    pattern_id = "data-processing-pipeline"
    if pattern_id not in library.patterns:
        print(f"Pattern {pattern_id} not found, adding it first.")
        library.patterns[pattern_id] = {
            "id": pattern_id,
            "name": "Data Processing Pipeline",
            "description": "A pipeline for processing data.",
            "structure": {
                "steps": [
                    {"id": "step1", "name": "Data Ingestion", "type": "input", "config": {}},
                    {"id": "step2", "name": "Data Cleaning", "type": "transform", "config": {}}
                ],
                "connections": [{"from": "step1", "to": "step2"}]
            },
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    # Create a new version with changes
    updated_structure = library.patterns[pattern_id]["structure"].copy()
    updated_structure["steps"].append({"id": "step3", "name": "Data Analysis", "type": "analysis", "config": {}})
    updated_structure["connections"].append({"from": "step2", "to": "step3"})
    library.version_pattern(pattern_id, "Added data analysis step", updated_structure)
    print(f"Created new version for {pattern_id}")
    
    # List versions
    versions_dict = library.list_pattern_versions(pattern_id)
    print(f"Versions of {pattern_id}: {versions_dict}")
    version_keys = list(versions_dict.keys())
    
    # Compare versions
    if len(version_keys) >= 2:
        diff = library.compare_pattern_versions(pattern_id, version_keys[0], version_keys[1])
        print(f"Differences between {version_keys[0]} and {version_keys[1]}: {diff}")
    
    # Rollback to previous version
    if len(version_keys) > 0:
        library.rollback_to_version(pattern_id, version_keys[0])
        print(f"Rolled back {pattern_id} to version {version_keys[0]}")
    
    # Get specific version
    if len(version_keys) > 0:
        old_version = library.get_pattern_version(pattern_id, version_keys[0])
        print(f"Retrieved version {version_keys[0]} details: {old_version.get('version_label')}")
    
    # Handle updated_at for contributed patterns to avoid KeyError
    for pattern_id in list(library.marketplace_patterns.keys()):
        if "updated_at" not in library.marketplace_patterns[pattern_id]:
            library.marketplace_patterns[pattern_id]["updated_at"] = datetime.now().isoformat()
    print("\nDemo completed. All patterns in marketplace have updated_at field.")

if __name__ == "__main__":
    run_demo()
