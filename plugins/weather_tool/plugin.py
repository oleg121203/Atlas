"""A simple weather tool plugin for Atlas."""

def get_weather(location: str) -> str:
    """Returns the weather forecast for a given location."""
    return f"The weather in {location} is sunny with a high of 25°C."

def register():
    """Registers the weather tool with the PluginManager."""
    return {
        "tools": [get_weather],
    }
