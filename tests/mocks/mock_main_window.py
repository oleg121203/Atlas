class MockMainWindow:
    """Mock main window class for testing."""
    
    def __init__(self):
        """Initialize mock window."""
        self._visible = True
        
    def show(self) -> None:
        """Mock show method."""
        self._visible = True
        
    def hide(self) -> None:
        """Mock hide method."""
        self._visible = False
        
    def isVisible(self) -> bool:
        """Mock isVisible method."""
        return self._visible
        
    def showMaximized(self) -> None:
        """Mock showMaximized method."""
        self._visible = True
        
    def showNormal(self) -> None:
        """Mock showNormal method."""
        self._visible = True
