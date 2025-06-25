from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MockPluginMetadata:
    """Mock PluginMetadata class for testing."""
    
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    
    def __post_init__(self):
        """Initialize metadata with default values if not provided."""
        if not self.dependencies:
            self.dependencies = []

    def __eq__(self, other):
        """Compare metadata objects."""
        if isinstance(other, MockPluginMetadata):
            return (
                self.name == other.name and
                self.version == other.version and
                self.description == other.description and
                self.author == other.author and
                self.dependencies == other.dependencies
            )
        return False
