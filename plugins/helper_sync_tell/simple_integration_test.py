#!/usr/bin/env python3
"""Simple integration test for Ultimate AI Assistant"""

import sys
import os
from pathlib import Path

#Add plugin to path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def main():
    try:
        #Test import
        from ultimate_ai_assistant import UltimateAIAssistant, register
        print("✅ Import successful")
        
        #Test registration
        assistant = register()
        print(f"✅ Registration: {type(assistant).__name__}")
        
        #Test basic functionality
        response = assistant("Test query for Atlas integration")
        print(f"✅ Response generated: {len(response)} chars")
        
        print("🎉 Ultimate AI Assistant ready for Atlas!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
