class MockMemoryManager:
    """Mock memory manager class for testing."""

    def __init__(self):
        """Initialize mock memory manager."""
        self.memory = []

    def add_memory(self, content: str):
        """Mock add_memory method."""
        self.memory.append(content)

    def get_memory(self) -> list:
        """Mock get_memory method."""
        return self.memory

    def clear_memory(self):
        """Mock clear_memory method."""
        self.memory.clear()
