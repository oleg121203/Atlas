import sys
import os

# Add parent directory to sys.path to resolve imports
directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(directory)
sys.path.append(parent_directory)

# Optionally, print the updated sys.path for debugging
print("Updated sys.path for test environment setup:")
for path in sys.path:
    print(f"  - {path}")

print("Test environment setup complete.")
