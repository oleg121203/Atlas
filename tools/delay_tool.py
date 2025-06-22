#!/usr/bin/env python3
"""
Delay Tool for adding pauses between actions
"""

import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DelayTool:
    """Tool for adding controlled delays between actions."""
    
    def __init__(self):
        self.name = "delay_tool"
        self.description = "Adds controlled delays between actions for better execution"
    
    def wait(self, duration: float = 1.0, **kwargs) -> Dict[str, Any]:
        """
        Wait for specified duration.
        
        Args:
            duration: Duration to wait in seconds (default: 1.0)
            
        Returns:
            Status of the delay operation
        """
        try:
            logger.info(f"⏱️ Waiting for {duration} seconds...")
            time.sleep(duration)
            logger.info(f"✅ Delay completed ({duration}s)")
            
            return {
                "status": "success",
                "message": f"Waited for {duration} seconds",
                "duration": duration,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Delay failed: {e}")
            return {
                "status": "error",
                "message": f"Delay failed: {str(e)}",
                "duration": duration,
                "timestamp": time.time()
            }
    
    def smart_wait(self, action_type: str = "general", **kwargs) -> Dict[str, Any]:
        """
        Smart wait with duration based on action type.
        
        Args:
            action_type: Type of action ("browser", "search", "click", "general")
            
        Returns:
            Status of the delay operation
        """
        # Define smart delays based on action type
        delays = {
            "browser": 2.0,      # Browser operations need more time
            "search": 1.5,       # Search operations need moderate time
            "click": 0.5,        # Click operations need minimal time
            "screenshot": 1.0,   # Screenshot operations need moderate time
            "general": 1.0       # Default delay
        }
        
        duration = delays.get(action_type, delays["general"])
        return self.wait(duration)
    
    def progressive_wait(self, step_number: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Progressive wait that increases with step number.
        
        Args:
            step_number: Current step number (1-based)
            
        Returns:
            Status of the delay operation
        """
        # Progressive delay: 1s for step 1, 1.5s for step 2, 2s for step 3, etc.
        duration = min(1.0 + (step_number - 1) * 0.5, 3.0)  # Cap at 3 seconds
        return self.wait(duration) 