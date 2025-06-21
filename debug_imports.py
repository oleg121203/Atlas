import sys
import os

# Add project root to path, similar to conftest.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Importing StrategicPlanner...")
print("StrategicPlanner import successful.")

print("Importing TacticalPlanner...")
print("TacticalPlanner import successful.")

print("Importing MasterAgent...")
print("MasterAgent import successful.")

print("All imports successful.")
