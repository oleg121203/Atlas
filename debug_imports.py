import sys
import os

# Add project root to path, similar to conftest.py
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Importing StrategicPlanner...")
from agents.planning.strategic_planner import StrategicPlanner
print("StrategicPlanner import successful.")

print("Importing TacticalPlanner...")
from agents.planning.tactical_planner import TacticalPlanner
print("TacticalPlanner import successful.")

print("Importing MasterAgent...")
from agents.master_agent import MasterAgent
print("MasterAgent import successful.")

print("All imports successful.")
