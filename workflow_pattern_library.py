from typing import Dict, List, Any, Optional, Tuple
import copy
import json
import os
from datetime import datetime

class WorkflowPatternLibrary:
    def __init__(self, library_path: Optional[str] = None):
        """
        Initialize the Workflow Pattern Library.

        Args:
            library_path (Optional[str]): Path to store/load the pattern library data.
        """
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        self.library_path = library_path or "workflow_patterns.json"
        self.marketplace_patterns: Dict[str, Dict[str, Any]] = {}
        self.marketplace_path = os.path.join(os.path.dirname(self.library_path), "marketplace_patterns.json")
        self.load_library()
        self.load_marketplace()

    def load_library(self) -> None:
        """
        Load the pattern library from a file if it exists.
        """
        if os.path.exists(self.library_path):
            try:
                with open(self.library_path, 'r') as f:
                    data = json.load(f)
                    self.patterns = data.get("patterns", {})
                    self.categories = data.get("categories", {})
                    self.tags = data.get("tags", {})
            except Exception as e:
                print(f"Error loading library: {e}")
                self.initialize_default_patterns()
        else:
            self.initialize_default_patterns()

    def initialize_default_patterns(self) -> None:
        """
        Initialize the library with some default workflow patterns.
        """
        self.patterns = {
            "etl_basic": {
                "name": "Basic ETL Pipeline",
                "description": "Extract, Transform, Load workflow for data processing.",
                "category": "Data Processing",
                "tags": ["ETL", "data", "pipeline"],
                "structure": {
                    "steps": [
                        {"id": 1, "name": "Extract", "type": "input", "config": {"source": "configurable"}},
                        {"id": 2, "name": "Transform", "type": "processing", "config": {"rules": "configurable"}},
                        {"id": 3, "name": "Load", "type": "output", "config": {"destination": "configurable"}}
                    ],
                    "connections": [
                        {"from": 1, "to": 2},
                        {"from": 2, "to": 3}
                    ]
                },
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "usage_count": 0
            },
            "ml_training": {
                "name": "Machine Learning Training Pipeline",
                "description": "Workflow for training machine learning models.",
                "category": "Machine Learning",
                "tags": ["ML", "training", "model"],
                "structure": {
                    "steps": [
                        {"id": 1, "name": "Data Ingestion", "type": "input", "config": {"source": "configurable"}},
                        {"id": 2, "name": "Data Preprocessing", "type": "processing", "config": {"steps": "configurable"}},
                        {"id": 3, "name": "Model Training", "type": "training", "config": {"algorithm": "configurable"}},
                        {"id": 4, "name": "Model Evaluation", "type": "evaluation", "config": {"metrics": "configurable"}},
                        {"id": 5, "name": "Model Deployment", "type": "output", "config": {"target": "configurable"}}
                    ],
                    "connections": [
                        {"from": 1, "to": 2},
                        {"from": 2, "to": 3},
                        {"from": 3, "to": 4},
                        {"from": 4, "to": 5}
                    ]
                },
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "usage_count": 0
            },
            "batch_processing": {
                "name": "Batch Processing Workflow",
                "description": "Workflow for processing data in batches.",
                "category": "Data Processing",
                "tags": ["batch", "data", "processing"],
                "structure": {
                    "steps": [
                        {"id": 1, "name": "Batch Input", "type": "input", "config": {"source": "configurable", "batch_size": "configurable"}},
                        {"id": 2, "name": "Batch Process", "type": "processing", "config": {"logic": "configurable"}},
                        {"id": 3, "name": "Batch Output", "type": "output", "config": {"destination": "configurable"}}
                    ],
                    "connections": [
                        {"from": 1, "to": 2},
                        {"from": 2, "to": 3}
                    ]
                },
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "usage_count": 0
            }
        }
        
        # Build categories and tags index
        self.categories = {}
        self.tags = {}
        for pattern_id, pattern in self.patterns.items():
            category = pattern.get("category", "Uncategorized")
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(pattern_id)
            
            for tag in pattern.get("tags", []):
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(pattern_id)

    def save_library(self) -> None:
        """
        Save the pattern library to a file.
        """
        data = {
            "patterns": self.patterns,
            "categories": self.categories,
            "tags": self.tags
        }
        try:
            with open(self.library_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving library: {e}")

    def add_pattern(self, pattern_id: str, name: str, description: str, category: str, 
                    tags: List[str], structure: Dict[str, Any], version: str = "1.0.0") -> bool:
        """
        Add a new workflow pattern to the library.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            name (str): Name of the pattern.
            description (str): Description of the pattern.
            category (str): Category of the pattern.
            tags (List[str]): List of tags associated with the pattern.
            structure (Dict[str, Any]): Structural definition of the workflow pattern.
            version (str): Version of the pattern.

        Returns:
            bool: True if pattern was added successfully, False if pattern_id already exists.
        """
        if pattern_id in self.patterns:
            return False
        
        now = datetime.now().isoformat()
        self.patterns[pattern_id] = {
            "name": name,
            "description": description,
            "category": category,
            "tags": tags,
            "structure": structure,
            "version": version,
            "created": now,
            "last_updated": now,
            "usage_count": 0
        }
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(pattern_id)
        
        for tag in tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(pattern_id)
        
        self.save_library()
        return True

    def update_pattern(self, pattern_id: str, name: Optional[str] = None, 
                       description: Optional[str] = None, category: Optional[str] = None, 
                       tags: Optional[List[str]] = None, structure: Optional[Dict[str, Any]] = None, 
                       version: Optional[str] = None) -> bool:
        """
        Update an existing workflow pattern in the library.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            name (Optional[str]): New name of the pattern.
            description (Optional[str]): New description of the pattern.
            category (Optional[str]): New category of the pattern.
            tags (Optional[List[str]]): New list of tags associated with the pattern.
            structure (Optional[Dict[str, Any]]): New structural definition of the workflow pattern.
            version (Optional[str]): New version of the pattern.

        Returns:
            bool: True if pattern was updated successfully, False if pattern_id doesn't exist.
        """
        if pattern_id not in self.patterns:
            return False
        
        pattern = self.patterns[pattern_id]
        old_category = pattern["category"]
        old_tags = pattern["tags"]
        
        if name is not None:
            pattern["name"] = name
        if description is not None:
            pattern["description"] = description
        if category is not None:
            if old_category in self.categories and pattern_id in self.categories[old_category]:
                self.categories[old_category].remove(pattern_id)
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(pattern_id)
            pattern["category"] = category
        if tags is not None:
            for tag in old_tags:
                if tag in self.tags and pattern_id in self.tags[tag]:
                    self.tags[tag].remove(pattern_id)
            for tag in tags:
                if tag not in self.tags:
                    self.tags[tag] = []
                self.tags[tag].append(pattern_id)
            pattern["tags"] = tags
        if structure is not None:
            pattern["structure"] = structure
        if version is not None:
            pattern["version"] = version
        
        pattern["last_updated"] = datetime.now().isoformat()
        self.save_library()
        return True

    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a workflow pattern from the library.

        Args:
            pattern_id (str): Unique identifier for the pattern.

        Returns:
            bool: True if pattern was deleted successfully, False if pattern_id doesn't exist.
        """
        if pattern_id not in self.patterns:
            return False
        
        pattern = self.patterns[pattern_id]
        category = pattern["category"]
        tags = pattern["tags"]
        
        if category in self.categories and pattern_id in self.categories[category]:
            self.categories[category].remove(pattern_id)
            if not self.categories[category]:
                del self.categories[category]
        
        for tag in tags:
            if tag in self.tags and pattern_id in self.tags[tag]:
                self.tags[tag].remove(pattern_id)
                if not self.tags[tag]:
                    del self.tags[tag]
        
        del self.patterns[pattern_id]
        self.save_library()
        return True

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific workflow pattern by ID.

        Args:
            pattern_id (str): Unique identifier for the pattern.

        Returns:
            Optional[Dict[str, Any]]: Pattern details if found, None otherwise.
        """
        return self.patterns.get(pattern_id)

    def list_patterns(self, category: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available workflow patterns, optionally filtered by category or tag.

        Args:
            category (Optional[str]): Category to filter by.
            tag (Optional[str]): Tag to filter by.

        Returns:
            List[Dict[str, Any]]: List of pattern summaries.
        """
        pattern_list = []
        pattern_ids = set()
        
        if category and tag:
            if category in self.categories and tag in self.tags:
                pattern_ids = set(self.categories[category]) & set(self.tags[tag])
        elif category:
            if category in self.categories:
                pattern_ids = set(self.categories[category])
        elif tag:
            if tag in self.tags:
                pattern_ids = set(self.tags[tag])
        else:
            pattern_ids = set(self.patterns.keys())
        
        for pid in pattern_ids:
            pattern = self.patterns[pid]
            pattern_list.append({
                "id": pid,
                "name": pattern.get("name", "Unnamed Pattern"),
                "description": pattern.get("description", ""),
                "category": pattern.get("category", "Uncategorized"),
                "tags": pattern.get("tags", []),
                "version": pattern.get("version", "1.0.0"),
                "usage_count": pattern.get("usage_count", 0),
                "last_updated": pattern.get("last_updated", pattern.get("updated_at", pattern.get("created_at", "Unknown")))
            })
        
        return sorted(pattern_list, key=lambda x: x["usage_count"], reverse=True)

    def list_categories(self) -> List[str]:
        """
        List all available categories in the library.

        Returns:
            List[str]: Sorted list of category names.
        """
        return sorted(list(self.categories.keys()))

    def list_tags(self) -> List[str]:
        """
        List all available tags in the library.

        Returns:
            List[str]: Sorted list of tag names.
        """
        return sorted(list(self.tags.keys()))

    def instantiate_pattern(self, pattern_id: str, custom_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Instantiate a workflow from a pattern with custom configuration.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            custom_config (Optional[Dict[str, Any]]): Custom configuration to apply to the pattern.

        Returns:
            Optional[Dict[str, Any]]: Instantiated workflow structure if pattern exists, None otherwise.
        """
        if pattern_id not in self.patterns:
            return None
        
        pattern = self.patterns[pattern_id]
        workflow_structure = pattern["structure"].copy()
        
        if custom_config:
            def apply_config(structure, config):
                for key, value in structure.items():
                    if isinstance(value, dict):
                        if key in config:
                            if isinstance(config[key], dict):
                                structure[key].update(config[key])
                            else:
                                structure[key] = config[key]
                        apply_config(value, config.get(key, {}))
                    elif key in config:
                        structure[key] = config[key]
                return structure
            
            workflow_structure = apply_config(workflow_structure, custom_config)
        
        self.patterns[pattern_id]["usage_count"] += 1
        self.patterns[pattern_id]["last_updated"] = datetime.now().isoformat()
        self.save_library()
        
        return {
            "name": pattern["name"],
            "description": pattern["description"],
            "based_on_pattern": pattern_id,
            "structure": workflow_structure,
            "created": datetime.now().isoformat()
        }

    def search_patterns(self, query: str) -> List[Dict[str, Any]]:
        """
        Search patterns by name, description, category, or tags.

        Args:
            query (str): Search query.

        Returns:
            List[Dict[str, Any]]: List of matching pattern summaries.
        """
        query_lower = query.lower()
        results = []
        
        for pattern_id, pattern in self.patterns.items():
            if (query_lower in pattern.get("name", "").lower() or 
                query_lower in pattern.get("description", "").lower() or 
                query_lower in pattern.get("category", "").lower() or 
                any(query_lower in tag.lower() for tag in pattern.get("tags", []))):
                results.append({
                    "id": pattern_id,
                    "name": pattern.get("name", "Unnamed Pattern"),
                    "description": pattern.get("description", ""),
                    "category": pattern.get("category", "Uncategorized"),
                    "tags": pattern.get("tags", []),
                    "version": pattern.get("version", "1.0.0"),
                    "usage_count": pattern.get("usage_count", 0),
                    "last_updated": pattern.get("last_updated", pattern.get("updated_at", pattern.get("created_at", "Unknown")))
                })
        
        return sorted(results, key=lambda x: x["usage_count"], reverse=True)

    def load_marketplace(self) -> None:
        """
        Load the marketplace patterns from a file if it exists.
        """
        if os.path.exists(self.marketplace_path):
            try:
                with open(self.marketplace_path, 'r') as f:
                    data = json.load(f)
                    self.marketplace_patterns = data.get("patterns", {})
            except Exception as e:
                print(f"Error loading marketplace: {e}")
                self.marketplace_patterns = {}
        else:
            self.marketplace_patterns = {}

    def save_marketplace(self) -> None:
        """
        Save the marketplace patterns to a file.
        """
        data = {
            "patterns": self.marketplace_patterns
        }
        try:
            with open(self.marketplace_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving marketplace: {e}")

    def contribute_pattern(self, pattern_id: str, name: str, description: str, category: str, tags: List[str], structure: Dict[str, Any], author: str, license: str = "MIT") -> bool:
        """
        Contribute a new pattern to the marketplace.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            name (str): Name of the pattern.
            description (str): Description of the pattern.
            category (str): Category of the pattern.
            tags (List[str]): Tags associated with the pattern.
            structure (Dict[str, Any]): Structural definition of the workflow pattern.
            author (str): Author of the pattern.
            license (str): License under which the pattern is shared (default: MIT).

        Returns:
            bool: True if contribution was successful, False otherwise.
        """
        now = datetime.now().isoformat()
        self.marketplace_patterns[pattern_id] = {
            "id": pattern_id,
            "name": name,
            "description": description,
            "category": category,
            "tags": tags,
            "structure": structure,
            "author": author,
            "license": license,
            "created_at": now,
            "updated_at": now,
            "rating": 0.0,
            "rating_count": 0,
            "usage_count": 0,
            "comments": []
        }
        self.save_marketplace()
        return True

    def update_contributed_pattern(self, pattern_id: str, name: Optional[str] = None, 
                                   description: Optional[str] = None, category: Optional[str] = None, 
                                   tags: Optional[List[str]] = None, structure: Optional[Dict[str, Any]] = None, 
                                   version: Optional[str] = None) -> bool:
        """
        Update an existing contributed pattern in the marketplace.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            name (Optional[str]): New name of the pattern.
            description (Optional[str]): New description of the pattern.
            category (Optional[str]): New category of the pattern.
            tags (Optional[List[str]]): New list of tags associated with the pattern.
            structure (Optional[Dict[str, Any]]): New structural definition of the workflow pattern.
            version (Optional[str]): New version of the pattern.

        Returns:
            bool: True if pattern was updated successfully, False if pattern_id doesn't exist.
        """
        if pattern_id not in self.marketplace_patterns:
            return False
        
        pattern = self.marketplace_patterns[pattern_id]
        
        if name is not None:
            pattern["name"] = name
        if description is not None:
            pattern["description"] = description
        if category is not None:
            pattern["category"] = category
        if tags is not None:
            pattern["tags"] = tags
        if structure is not None:
            pattern["structure"] = structure
        if version is not None:
            pattern["version"] = version
        
        pattern["updated_at"] = datetime.now().isoformat()
        self.save_marketplace()
        return True

    def delete_contributed_pattern(self, pattern_id: str) -> bool:
        """
        Delete a contributed pattern from the marketplace.

        Args:
            pattern_id (str): Unique identifier for the pattern.

        Returns:
            bool: True if pattern was deleted successfully, False if pattern_id doesn't exist.
        """
        if pattern_id not in self.marketplace_patterns:
            return False
        
        del self.marketplace_patterns[pattern_id]
        self.save_marketplace()
        return True

    def get_contributed_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific contributed pattern by ID.

        Args:
            pattern_id (str): Unique identifier for the pattern.

        Returns:
            Optional[Dict[str, Any]]: Pattern details if found, None otherwise.
        """
        return self.marketplace_patterns.get(pattern_id)

    def list_contributed_patterns(self, category: Optional[str] = None, tag: Optional[str] = None, 
                                  author: Optional[str] = None, sort_by: str = "usage_count") -> List[Dict[str, Any]]:
        """
        List available contributed patterns, optionally filtered by category, tag, or author.

        Args:
            category (Optional[str]): Category to filter by.
            tag (Optional[str]): Tag to filter by.
            author (Optional[str]): Author to filter by.
            sort_by (str): Field to sort by ('usage_count', 'rating', 'last_updated').

        Returns:
            List[Dict[str, Any]]: List of pattern summaries.
        """
        pattern_list = []
        
        for pattern_id, pattern in self.marketplace_patterns.items():
            if category and pattern["category"] != category:
                continue
            if tag and tag not in pattern["tags"]:
                continue
            if author and pattern["author"] != author:
                continue
            
            pattern_list.append({
                "id": pattern_id,
                "name": pattern["name"],
                "description": pattern["description"],
                "author": pattern["author"],
                "version": pattern.get("version", "1.0.0"),
                "license": pattern["license"],
                "usage_count": pattern["usage_count"],
                "rating": pattern["rating"],
                "rating_count": pattern["rating_count"],
                "last_updated": pattern.get("updated_at", pattern.get("created_at", "Unknown"))
            })
        
        return sorted(pattern_list, key=lambda x: x[sort_by], reverse=True)

    def search_contributed_patterns(self, query: str) -> List[Dict[str, Any]]:
        """
        Search contributed patterns by name, description, category, tags, or author.

        Args:
            query (str): Search query.

        Returns:
            List[Dict[str, Any]]: List of matching pattern summaries.
        """
        query_lower = query.lower()
        results = []
        
        for pattern_id, pattern in self.marketplace_patterns.items():
            if (query_lower in pattern["name"].lower() or 
                query_lower in pattern["description"].lower() or 
                query_lower in pattern["category"].lower() or 
                query_lower in pattern["author"].lower() or 
                any(query_lower in tag.lower() for tag in pattern["tags"])):
                results.append({
                    "id": pattern_id,
                    "name": pattern["name"],
                    "description": pattern["description"],
                    "author": pattern["author"],
                    "version": pattern.get("version", "1.0.0"),
                    "license": pattern["license"],
                    "usage_count": pattern["usage_count"],
                    "rating": pattern["rating"],
                    "rating_count": pattern["rating_count"],
                    "last_updated": pattern.get("updated_at", pattern.get("created_at", "Unknown"))
                })
        
        return sorted(results, key=lambda x: x["usage_count"], reverse=True)

    def instantiate_contributed_pattern(self, pattern_id: str, custom_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Instantiate a workflow from a contributed pattern with custom configuration.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            custom_config (Optional[Dict[str, Any]]): Custom configuration to apply to the pattern.

        Returns:
            Optional[Dict[str, Any]]: Instantiated workflow structure if pattern exists, None otherwise.
        """
        if pattern_id not in self.marketplace_patterns:
            return None
        
        pattern = self.marketplace_patterns[pattern_id]
        workflow_structure = pattern["structure"].copy()
        
        if custom_config:
            def apply_config(structure, config):
                for key, value in structure.items():
                    if isinstance(value, dict):
                        if key in config:
                            if isinstance(config[key], dict):
                                structure[key].update(config[key])
                            else:
                                structure[key] = config[key]
                        apply_config(value, config.get(key, {}))
                    elif key in config:
                        structure[key] = config[key]
                return structure
            
            workflow_structure = apply_config(workflow_structure, custom_config)
        
        self.marketplace_patterns[pattern_id]["usage_count"] += 1
        self.marketplace_patterns[pattern_id]["updated_at"] = datetime.now().isoformat()
        self.save_marketplace()
        
        return {
            "name": pattern["name"],
            "description": pattern["description"],
            "based_on_pattern": pattern_id,
            "author": pattern["author"],
            "license": pattern["license"],
            "structure": workflow_structure,
            "created": datetime.now().isoformat()
        }

    def rate_contributed_pattern(self, pattern_id: str, rating: float) -> bool:
        """
        Rate a contributed pattern.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            rating (float): Rating value (e.g., 1.0 to 5.0).

        Returns:
            bool: True if rating was recorded successfully, False if pattern_id doesn't exist.
        """
        if pattern_id not in self.marketplace_patterns:
            return False
        
        pattern = self.marketplace_patterns[pattern_id]
        current_rating = pattern["rating"]
        current_count = pattern["rating_count"]
        
        new_count = current_count + 1
        new_rating = ((current_rating * current_count) + rating) / new_count
        
        pattern["rating"] = round(new_rating, 2)
        pattern["rating_count"] = new_count
        pattern["updated_at"] = datetime.now().isoformat()
        self.save_marketplace()
        return True

    def comment_on_contributed_pattern(self, pattern_id: str, comment: str, author: str) -> bool:
        """
        Add a comment to a contributed pattern.

        Args:
            pattern_id (str): Unique identifier for the pattern.
            comment (str): Comment text.
            author (str): Author of the comment.

        Returns:
            bool: True if comment was added successfully, False if pattern_id doesn't exist.
        """
        if pattern_id not in self.marketplace_patterns:
            return False
        
        pattern = self.marketplace_patterns[pattern_id]
        pattern["comments"].append({
            "text": comment,
            "author": author,
            "timestamp": datetime.now().isoformat()
        })
        pattern["updated_at"] = datetime.now().isoformat()
        self.save_marketplace()
        return True

    def customize_pattern(self, pattern_id: str, customizations: Dict[str, Any], save_as_new: bool = False, new_pattern_id: Optional[str] = None) -> Optional[str]:
        """
        Customize an existing pattern with specific modifications.

        Args:
            pattern_id (str): ID of the pattern to customize.
            customizations (Dict[str, Any]): Dictionary of customizations to apply to the pattern structure.
            save_as_new (bool): If True, save the customized pattern as a new pattern.
            new_pattern_id (Optional[str]): ID for the new customized pattern if saving as new.

        Returns:
            Optional[str]: ID of the new customized pattern if saved as new, None otherwise.
        """
        if pattern_id not in self.patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library.")

        pattern = copy.deepcopy(self.patterns[pattern_id])
        self._apply_customizations(pattern["structure"], customizations)

        if save_as_new:
            if not new_pattern_id:
                new_pattern_id = f"custom_{pattern_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if new_pattern_id in self.patterns:
                raise ValueError(f"New pattern ID {new_pattern_id} already exists in library.")

            self.patterns[new_pattern_id] = pattern
            self.patterns[new_pattern_id]["id"] = new_pattern_id
            self.patterns[new_pattern_id]["name"] = f"Customized {pattern['name']}"
            self.patterns[new_pattern_id]["description"] = f"Customized version of {pattern['name']} created on {datetime.now().strftime('%Y-%m-%d')}"
            self.patterns[new_pattern_id]["category"] = f"Custom {pattern['category']}"
            self.patterns[new_pattern_id]["tags"].append("custom")
            self._update_indices(new_pattern_id, self.patterns[new_pattern_id])
            self.save_library()
            return new_pattern_id
        else:
            self.patterns[pattern_id]["structure"] = pattern["structure"]
            self.patterns[pattern_id]["description"] += " (Customized)"
            self.patterns[pattern_id]["tags"].append("customized")
            self._update_indices(pattern_id, self.patterns[pattern_id])
            self.save_library()
            return None

    def share_pattern(self, pattern_id: str, destination: str, format: str = "json") -> bool:
        """
        Share a pattern by exporting it to a specified destination.

        Args:
            pattern_id (str): ID of the pattern to share.
            destination (str): Destination path or URL to share the pattern to.
            format (str): Format to export the pattern in (default: json).

        Returns:
            bool: True if sharing was successful, False otherwise.
        """
        if pattern_id not in self.patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library.")

        pattern = self.patterns[pattern_id]
        export_data = {
            "id": pattern_id,
            "name": pattern["name"],
            "description": pattern["description"],
            "category": pattern["category"],
            "tags": pattern["tags"],
            "structure": pattern["structure"]
        }

        try:
            if format.lower() == "json":
                with open(destination, 'w') as f:
                    json.dump(export_data, f, indent=2)
            elif format.lower() == "yaml":
                import yaml
                with open(destination, 'w') as f:
                    yaml.safe_dump(export_data, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            return True
        except Exception as e:
            print(f"Error sharing pattern: {e}")
            return False

    def import_shared_pattern(self, source: str, format: str = "json", pattern_id: Optional[str] = None) -> str:
        """
        Import a shared pattern from a specified source.

        Args:
            source (str): Source path or URL of the shared pattern.
            format (str): Format of the shared pattern (default: json).
            pattern_id (Optional[str]): ID to assign to the imported pattern, if None use the original ID.

        Returns:
            str: ID of the imported pattern.
        """
        try:
            if format.lower() == "json":
                with open(source, 'r') as f:
                    import_data = json.load(f)
            elif format.lower() == "yaml":
                import yaml
                with open(source, 'r') as f:
                    import_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported import format: {format}")

            original_id = import_data.get("id", f"imported_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            new_id = pattern_id if pattern_id else original_id

            if new_id in self.patterns:
                raise ValueError(f"Pattern ID {new_id} already exists in library.")

            self.patterns[new_id] = {
                "id": new_id,
                "name": import_data.get("name", "Imported Pattern"),
                "description": import_data.get("description", "Imported pattern with no description."),
                "category": import_data.get("category", "Imported"),
                "tags": import_data.get("tags", ["imported"]),
                "structure": import_data.get("structure", {"steps": [], "connections": []})
            }
            self._update_indices(new_id, self.patterns[new_id])
            self.save_library()
            return new_id
        except Exception as e:
            raise RuntimeError(f"Error importing pattern: {e}")

    def _apply_customizations(self, structure: Dict[str, Any], customizations: Dict[str, Any]) -> None:
        """
        Apply customizations to a pattern structure.

        Args:
            structure (Dict[str, Any]): Pattern structure to customize.
            customizations (Dict[str, Any]): Customizations to apply.
        """
        for key, value in customizations.items():
            if isinstance(value, dict):
                if key in structure:
                    self._apply_customizations(structure[key], value)
                else:
                    structure[key] = value
            else:
                structure[key] = value

    def _update_indices(self, pattern_id: str, pattern: Dict[str, Any]) -> None:
        """
        Update the category and tag indices for a pattern.

        Args:
            pattern_id (str): ID of the pattern.
            pattern (Dict[str, Any]): Pattern data.
        """
        category = pattern["category"]
        tags = pattern["tags"]

        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(pattern_id)

        for tag in tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(pattern_id)

    def validate_pattern_structure(self, structure: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the structure of a workflow pattern to ensure it meets required criteria.

        Args:
            structure (Dict[str, Any]): The pattern structure to validate.

        Returns:
            Tuple[bool, List[str]]: A tuple of (is_valid, errors) where is_valid indicates if the structure is valid,
                                    and errors is a list of error messages if invalid.
        """
        errors = []
        if not isinstance(structure, dict):
            errors.append("Pattern structure must be a dictionary.")
            return False, errors

        if "steps" not in structure or not isinstance(structure["steps"], list):
            errors.append("Pattern structure must contain a 'steps' list.")
        else:
            for step_idx, step in enumerate(structure["steps"]):
                if not isinstance(step, dict):
                    errors.append(f"Step {step_idx} is not a dictionary.")
                    continue
                if "id" not in step or not isinstance(step.get("id"), (int, str)):
                    errors.append(f"Step {step_idx} must have a valid 'id' field.")
                if "name" not in step or not isinstance(step.get("name"), str):
                    errors.append(f"Step {step_idx} must have a valid 'name' field.")
                if "type" not in step or not isinstance(step.get("type"), str):
                    errors.append(f"Step {step_idx} must have a valid 'type' field.")
                if "config" not in step or not isinstance(step.get("config"), dict):
                    errors.append(f"Step {step_idx} must have a valid 'config' dictionary.")

        if "connections" not in structure or not isinstance(structure["connections"], list):
            errors.append("Pattern structure must contain a 'connections' list.")
        else:
            step_ids = {step.get("id") for step in structure.get("steps", []) if isinstance(step, dict) and "id" in step}
            for conn_idx, conn in enumerate(structure["connections"]):
                if not isinstance(conn, dict):
                    errors.append(f"Connection {conn_idx} is not a dictionary.")
                    continue
                if "from" not in conn or conn.get("from") not in step_ids:
                    errors.append(f"Connection {conn_idx} has invalid 'from' field.")
                if "to" not in conn or conn.get("to") not in step_ids:
                    errors.append(f"Connection {conn_idx} has invalid 'to' field.")

        return len(errors) == 0, errors

    def validate_pattern(self, pattern_id: str) -> Tuple[bool, List[str]]:
        """
        Validate a pattern in the library or marketplace by its ID.

        Args:
            pattern_id (str): ID of the pattern to validate.

        Returns:
            Tuple[bool, List[str]]: A tuple of (is_valid, errors) where is_valid indicates if the pattern is valid,
                                    and errors is a list of error messages if invalid.
        """
        pattern = None
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
        elif pattern_id in self.marketplace_patterns:
            pattern = self.marketplace_patterns[pattern_id]
        else:
            return False, [f"Pattern {pattern_id} not found in library or marketplace."]

        return self.validate_pattern_structure(pattern["structure"])

    def test_pattern_execution(self, pattern_id: str, test_config: Optional[Dict[str, Any]] = None, test_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Test the execution of a pattern with provided configuration and test data.

        Args:
            pattern_id (str): ID of the pattern to test.
            test_config (Optional[Dict[str, Any]]): Custom configuration for testing the pattern.
            test_data (Optional[List[Dict[str, Any]]]): Test input data for the pattern steps.

        Returns:
            Dict[str, Any]: Test results including status, execution log, and any errors.
        """
        if pattern_id not in self.patterns and pattern_id not in self.marketplace_patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library or marketplace.")

        pattern = self.patterns.get(pattern_id, self.marketplace_patterns.get(pattern_id))
        is_valid, validation_errors = self.validate_pattern(pattern_id)
        if not is_valid:
            return {
                "status": "failed",
                "reason": "validation_failed",
                "errors": validation_errors
            }

        execution_log = []
        errors = []
        try:
            # Simulate execution of each step with test config and data
            workflow = self.instantiate_pattern(pattern_id, test_config or {})
            execution_log.append(f"Instantiated workflow: {workflow['name']}")

            # Simulate processing test data through steps
            if test_data:
                for data_idx, data_item in enumerate(test_data):
                    execution_log.append(f"Processing test data item {data_idx + 1}")
                    for step in workflow["structure"]["steps"]:
                        step_name = step.get("name", f"Step {step.get('id')}")
                        execution_log.append(f"  - Executing {step_name}")
                        # Here we would simulate the step execution with data_item
                        # For now, just log that we attempted execution
                        execution_log.append(f"    - Input: {data_item}")
                        execution_log.append(f"    - Config: {step.get('config', {})}")
                        execution_log.append(f"    - Result: Simulated success")
            else:
                execution_log.append("No test data provided, skipping step execution simulation.")

            return {
                "status": "success",
                "execution_log": execution_log,
                "errors": []
            }
        except Exception as e:
            errors.append(str(e))
            execution_log.append(f"Execution failed: {e}")
            return {
                "status": "failed",
                "reason": "execution_error",
                "execution_log": execution_log,
                "errors": errors
            }

    def version_pattern(self, pattern_id: str, change_description: str, updated_structure: Optional[Dict[str, Any]] = None, version_label: Optional[str] = None) -> str:
        """
        Create a new version of a pattern with a change description and optional updated structure.

        Args:
            pattern_id: ID of the pattern to version.
            change_description: Description of changes made in this version.
            updated_structure: Optional updated structure for the pattern.
            version_label: Optional label for the new version.

        Returns:
            New version identifier.

        Raises:
            KeyError: If the pattern_id is not found.
            ValueError: If the version_label already exists for the pattern.
        """
        if pattern_id not in self.patterns and pattern_id not in self.marketplace_patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library or marketplace.")
        pattern_source = self.patterns if pattern_id in self.patterns else self.marketplace_patterns
        current_version = pattern_source[pattern_id].get("version", "1.0.0")
        version_parts = current_version.split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        new_version = ".".join(version_parts)
        if "versions" not in pattern_source[pattern_id] or not isinstance(pattern_source[pattern_id]["versions"], dict):
            pattern_source[pattern_id]["versions"] = {}
        old_snapshot = copy.deepcopy(pattern_source[pattern_id])
        pattern_source[pattern_id]["versions"][current_version] = {
            "snapshot": old_snapshot,
            "change_description": "Previous version",
            "timestamp": pattern_source[pattern_id].get("updated_at", pattern_source[pattern_id].get("created_at", datetime.now().isoformat())),
            "version_label": current_version
        }
        if updated_structure:
            pattern_source[pattern_id]["structure"] = updated_structure
        pattern_source[pattern_id]["version"] = new_version
        pattern_source[pattern_id]["updated_at"] = datetime.now().isoformat()
        if version_label is None:
            version_label = new_version
        elif any(v.get("version_label", "") == version_label for v in pattern_source[pattern_id]["versions"].values()):
            raise ValueError(f"Version label {version_label} already exists for pattern {pattern_id}.")
        pattern_source[pattern_id]["versions"][new_version] = {
            "label": f"rollback_to_{version_label}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "changes": f"Rollback to version {version_label}",
            "structure": copy.deepcopy(pattern_source[pattern_id]["structure"]),
            "metadata": {
                "name": pattern_source[pattern_id]["name"],
                "description": pattern_source[pattern_id]["description"],
                "category": pattern_source[pattern_id].get("category", "Uncategorized"),
                "tags": copy.deepcopy(pattern_source[pattern_id].get("tags", []))
            }
        }

        if pattern_id in self.patterns:
            self.save_library()
        else:
            self.save_marketplace()
        return new_version

    def list_pattern_versions(self, pattern_id: str) -> List[Dict[str, Any]]:
        """
        List all versions of a pattern.

        Args:
            pattern_id (str): ID of the pattern to list versions for.

        Returns:
            List[Dict[str, Any]]: List of version information dictionaries.
        """
        if pattern_id not in self.patterns and pattern_id not in self.marketplace_patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library or marketplace.")

        pattern_source = self.patterns if pattern_id in self.patterns else self.marketplace_patterns
        return pattern_source[pattern_id].get("versions", [])

    def get_pattern_version(self, pattern_id: str, version_label: str) -> Dict[str, Any]:
        """
        Retrieve a specific version of a pattern by its label or identifier.

        Args:
            pattern_id: ID of the pattern.
            version_label: Label or identifier of the version to retrieve.

        Returns:
            Version details including structure and metadata.

        Raises:
            KeyError: If pattern or version is not found.
        """
        if pattern_id not in self.patterns and pattern_id not in self.marketplace_patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library or marketplace.")
        pattern_source = self.patterns if pattern_id in self.patterns else self.marketplace_patterns
        versions = pattern_source[pattern_id].get("versions", {})
        if not isinstance(versions, dict):
            raise ValueError(f"Versions for pattern {pattern_id} is not in the expected format.")
        for version_id, version_data in versions.items():
            if version_data.get("version_label", "") == version_label or version_id == version_label:
                return version_data
        raise KeyError(f"Version {version_label} not found for pattern {pattern_id}.")

    def rollback_to_version(self, pattern_id: str, version_label: str) -> bool:
        """
        Roll back a pattern to a specific version.

        Args:
            pattern_id (str): ID of the pattern to roll back.
            version_label (str): Version label to roll back to.

        Returns:
            bool: True if rollback was successful, False otherwise.
        """
        if pattern_id not in self.patterns and pattern_id not in self.marketplace_patterns:
            raise KeyError(f"Pattern {pattern_id} not found in library or marketplace.")

        pattern_source = self.patterns if pattern_id in self.patterns else self.marketplace_patterns
        version_data = self.get_pattern_version(pattern_id, version_label)

        # Handle different version data structures
        snapshot = version_data.get("snapshot", version_data)
        metadata = snapshot if "id" in snapshot else version_data.get("metadata", {})

        pattern_source[pattern_id]["structure"] = copy.deepcopy(snapshot.get("structure", {}))
        pattern_source[pattern_id]["name"] = metadata.get("name", "Unnamed Pattern")
        pattern_source[pattern_id]["description"] = metadata.get("description", "")
        pattern_source[pattern_id]["category"] = metadata.get("category", "Uncategorized")
        pattern_source[pattern_id]["tags"] = copy.deepcopy(metadata.get("tags", []))
        pattern_source[pattern_id]["updated_at"] = datetime.now().isoformat()
        pattern_source[pattern_id]["versions"][f"rollback_to_{version_label}_{datetime.now().strftime('%Y%m%d%H%M%S')}"] = {
            "label": f"rollback_to_{version_label}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "changes": f"Rollback to version {version_label}",
            "structure": copy.deepcopy(snapshot.get("structure", {})),
            "metadata": {
                "name": metadata.get("name", "Unnamed Pattern"),
                "description": metadata.get("description", ""),
                "category": metadata.get("category", "Uncategorized"),
                "tags": copy.deepcopy(metadata.get("tags", []))
            }
        }

        if pattern_id in self.patterns:
            self.save_library()
        else:
            self.save_marketplace()
        return True

    def compare_pattern_versions(self, pattern_id: str, version_label1: str, version_label2: str) -> Dict[str, Any]:
        """
        Compare two versions of a pattern to highlight differences.

        Args:
            pattern_id (str): ID of the pattern.
            version_label1 (str): First version label to compare.
            version_label2 (str): Second version label to compare.

        Returns:
            Dict[str, Any]: Comparison results including differences in structure and metadata.
        """
        version1 = self.get_pattern_version(pattern_id, version_label1)
        version2 = self.get_pattern_version(pattern_id, version_label2)

        def deep_compare(obj1: Any, obj2: Any, path: str = "") -> List[str]:
            differences = []
            if isinstance(obj1, dict) and isinstance(obj2, dict):
                for key in set(obj1.keys()) | set(obj2.keys()):
                    new_path = f"{path}.{key}" if path else key
                    if key not in obj1:
                        differences.append(f"{new_path}: Missing in version1")
                    elif key not in obj2:
                        differences.append(f"{new_path}: Missing in version2")
                    else:
                        differences.extend(deep_compare(obj1[key], obj2[key], new_path))
            elif isinstance(obj1, list) and isinstance(obj2, list):
                if len(obj1) != len(obj2):
                    differences.append(f"{path}: Lists have different lengths ({len(obj1)} vs {len(obj2)})")
                else:
                    for i in range(len(obj1)):
                        new_path = f"{path}[{i}]"
                        differences.extend(deep_compare(obj1[i], obj2[i], new_path))
            elif obj1 != obj2:
                differences.append(f"{path}: Values differ ({obj1} vs {obj2})")
            return differences

        # Handle different version data structures
        structure1 = version1.get("snapshot", {}).get("structure", version1.get("structure", {}))
        structure2 = version2.get("snapshot", {}).get("structure", version2.get("structure", {}))
        metadata1 = version1.get("snapshot", version1.get("metadata", {}))
        metadata2 = version2.get("snapshot", version2.get("metadata", {}))

        structure_diff = deep_compare(structure1, structure2, "structure")
        metadata_diff = deep_compare(metadata1, metadata2, "metadata")

        return {
            "version1_label": version_label1,
            "version2_label": version_label2,
            "structure_differences": structure_diff,
            "metadata_differences": metadata_diff,
            "timestamp1": version1.get("timestamp", ""),
            "timestamp2": version2.get("timestamp", ""),
            "changes1": version1.get("change_description", version1.get("changes", "")),
            "changes2": version2.get("change_description", version2.get("changes", ""))
        }
