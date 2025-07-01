# Placeholder for MemoryManager to stabilize application launch


class MemoryManager:
    def __init__(self):
        self.data = {}

    def store(self, key, value):
        self.data[key] = value

    def retrieve(self, key, default=None):
        return self.data.get(key, default)

    def clear(self):
        self.data.clear()
