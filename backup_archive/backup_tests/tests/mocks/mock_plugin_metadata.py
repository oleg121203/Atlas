from dataclasses import dataclass
from typing import List


@dataclass
class MockPluginMetadata:
    """Mock plugin metadata with version constraint support."""

    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = None
    min_app_version: str = None
    max_app_version: str = None
    icon: str = None
    tags: List[str] = None

    def __post_init__(self):
        """Initialize metadata with default values if not provided."""
        if not self.dependencies:
            self.dependencies = []
        if not self.tags:
            self.tags = []

    def __eq__(self, other):
        """Compare metadata objects."""
        if isinstance(other, MockPluginMetadata):
            return (
                self.name == other.name
                and self.version == other.version
                and self.description == other.description
                and self.author == other.author
                and self.dependencies == other.dependencies
                and self.min_app_version == other.min_app_version
                and self.max_app_version == other.max_app_version
                and self.icon == other.icon
                and self.tags == other.tags
            )
        return False

    def get_name(self) -> str:
        return self.name

    def get_version(self) -> str:
        return self.version

    def get_description(self) -> str:
        return self.description

    def get_author(self) -> str:
        return self.author

    def get_dependencies(self) -> List[str]:
        return self.dependencies

    def get_min_app_version(self) -> str:
        return self.min_app_version

    def get_max_app_version(self) -> str:
        return self.max_app_version

    def get_icon(self) -> str:
        return self.icon

    def get_tags(self) -> List[str]:
        return self.tags
