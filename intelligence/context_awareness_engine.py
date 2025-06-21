import subprocess
import os
from typing import Optional

from utils.logger import get_logger

class ContextAwarenessEngine:
    """Monitors the user's environment to build a dynamic understanding of their workflow."""

    def __init__(self, project_root: str):
        self.logger = get_logger(self.__class__.__name__)
        if not os.path.isdir(project_root):
            raise ValueError(f"Project root path does not exist or is not a directory: {project_root}")
        self.project_root = project_root
        self.logger.info(f"Context Awareness Engine initialized for project root: {self.project_root}")

    def get_current_context(self) -> dict:
        """Gathers all available context about the user's environment."""
        context = {
            "git_branch": self.get_git_branch()
            # Future context sources will be added here
        }
        return context

    def get_git_branch(self) -> Optional[str]:
        """Determines the current Git branch of the project."""
        git_dir = os.path.join(self.project_root, '.git')
        if not os.path.isdir(git_dir):
            self.logger.warning("Not a Git repository. Cannot determine branch.")
            return None

        try:
            # Ensure the command is run within the project's root directory
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            branch_name = result.stdout.strip()
            self.logger.info(f"Detected current Git branch: {branch_name}")
            return branch_name
        except FileNotFoundError:
            self.logger.error("Git command not found. Is Git installed and in the system's PATH?")
            return None
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to determine Git branch. Error: {e.stderr.strip()}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while getting Git branch: {e}", exc_info=True)
            return None
