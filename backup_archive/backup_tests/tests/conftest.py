import os
import sys

# Set an environment variable to indicate that the code is running in a test environment.
# This is used by other modules (like the logger) to change their behavior during tests.
os.environ["ATLAS_TESTING"] = "1"

# Add the project root to the Python path to allow for absolute imports
# of the project's modules in test files.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
