"""
Git Integration Plugin for Atlas.

This plugin provides comprehensive git operations including:
- Repository status and information
- Commit operations
- Branch management
- Remote operations
- Conflict resolution assistance
"""

import asyncio
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional

from core.plugin_system import PluginBase

logger = logging.getLogger(__name__)


class GitIntegrationPlugin(PluginBase):
    """
    Comprehensive Git integration plugin for Atlas.

    Provides git operations through a clean API with error handling,
    async support, and integration with the Atlas event system.
    """

    def __init__(self, name: str = "git_integration", version: str = "1.0.0"):
        """Initialize the Git integration plugin."""
        super().__init__(name, version)
        self.current_repo_path = None
        self._git_available = self._check_git_availability()

    def _check_git_availability(self) -> bool:
        """Check if git is available on the system."""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Git not found on system")
            return False

    async def _run_git_command(
        self, command: List[str], cwd: Optional[str] = None, timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Run a git command asynchronously.

        Args:
            command: Git command as a list of strings
            cwd: Working directory for the command
            timeout: Command timeout in seconds

        Returns:
            Dict containing command result, output, and error information
        """
        if not self._git_available:
            return {
                "success": False,
                "error": "Git is not available on this system",
                "output": "",
                "stderr": "",
            }

        try:
            # Use the current repository path if no cwd specified
            working_dir = cwd or self.current_repo_path or os.getcwd()

            process = await asyncio.create_subprocess_exec(
                "git",
                *command,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "output": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "command": " ".join(["git"] + command),
            }

            if not result["success"]:
                logger.warning(
                    f"Git command failed: {result['command']}, Error: {result['stderr']}"
                )
            else:
                logger.debug(f"Git command successful: {result['command']}")

            return result

        except asyncio.TimeoutError:
            logger.error(f"Git command timed out: git {' '.join(command)}")
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "output": "",
                "stderr": "",
                "command": " ".join(["git"] + command),
            }
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "stderr": "",
                "command": " ".join(["git"] + command),
            }

    def initialize(self) -> None:
        """Initialize the plugin and detect current repository."""
        super().initialize()
        logger.info("Initializing Git integration plugin")

        # Try to detect current git repository synchronously
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=os.getcwd(),
            )
            if result.returncode == 0:
                self.current_repo_path = result.stdout.strip()
                logger.info(f"Detected git repository at: {self.current_repo_path}")
            else:
                logger.debug("No git repository detected in current directory")
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            logger.debug("No git repository detected in current directory")

    async def get_status(self, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get git repository status.

        Args:
            repo_path: Optional path to repository

        Returns:
            Repository status information
        """
        result = await self._run_git_command(["status", "--porcelain"], cwd=repo_path)

        if not result["success"]:
            return result

        # Parse status output
        files = {"modified": [], "added": [], "deleted": [], "untracked": []}

        for line in result["output"].split("\n"):
            if not line.strip():
                continue

            status = line[:2]
            filename = line[3:]

            if status.startswith("M"):
                files["modified"].append(filename)
            elif status.startswith("A"):
                files["added"].append(filename)
            elif status.startswith("D"):
                files["deleted"].append(filename)
            elif status.startswith("??"):
                files["untracked"].append(filename)

        # Get branch information
        branch_result = await self._run_git_command(
            ["branch", "--show-current"], cwd=repo_path
        )
        current_branch = (
            branch_result["output"] if branch_result["success"] else "unknown"
        )

        return {
            "success": True,
            "current_branch": current_branch,
            "files": files,
            "has_changes": any(files.values()),
            "raw_output": result["output"],
        }

    async def commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        repo_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a git commit.

        Args:
            message: Commit message
            files: Optional list of files to commit (commits all if None)
            repo_path: Optional path to repository

        Returns:
            Commit operation result
        """
        if not message.strip():
            return {"success": False, "error": "Commit message cannot be empty"}

        commands = []

        # Add files
        if files:
            for file in files:
                commands.append(["add", file])
        else:
            commands.append(["add", "."])

        # Create commit
        commands.append(["commit", "-m", message])

        # Execute commands
        for command in commands:
            result = await self._run_git_command(command, cwd=repo_path)
            if not result["success"]:
                return result

        return {
            "success": True,
            "message": f"Successfully committed: {message}",
            "output": result["output"],
        }

    async def create_branch(
        self, branch_name: str, checkout: bool = True, repo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new git branch.

        Args:
            branch_name: Name of the new branch
            checkout: Whether to checkout the new branch immediately
            repo_path: Optional path to repository

        Returns:
            Branch creation result
        """
        if not branch_name.strip():
            return {"success": False, "error": "Branch name cannot be empty"}

        # Create branch
        command = (
            ["checkout", "-b", branch_name] if checkout else ["branch", branch_name]
        )
        result = await self._run_git_command(command, cwd=repo_path)

        if result["success"]:
            action = "created and checked out" if checkout else "created"
            result["message"] = f"Successfully {action} branch: {branch_name}"

        return result

    async def switch_branch(
        self, branch_name: str, repo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Switch to an existing branch.

        Args:
            branch_name: Name of the branch to switch to
            repo_path: Optional path to repository

        Returns:
            Branch switch result
        """
        result = await self._run_git_command(["checkout", branch_name], cwd=repo_path)

        if result["success"]:
            result["message"] = f"Successfully switched to branch: {branch_name}"

        return result

    async def get_branches(self, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of all branches.

        Args:
            repo_path: Optional path to repository

        Returns:
            List of branches
        """
        result = await self._run_git_command(["branch", "-a"], cwd=repo_path)

        if not result["success"]:
            return result

        branches = []
        current_branch = None

        for line in result["output"].split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("* "):
                current_branch = line[2:]
                branches.append(current_branch)
            else:
                branches.append(line)

        return {"success": True, "branches": branches, "current_branch": current_branch}

    async def pull(self, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Pull changes from remote repository.

        Args:
            repo_path: Optional path to repository

        Returns:
            Pull operation result
        """
        result = await self._run_git_command(["pull"], cwd=repo_path)

        if result["success"]:
            result["message"] = "Successfully pulled changes from remote"

        return result

    async def push(
        self, branch: Optional[str] = None, repo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Push changes to remote repository.

        Args:
            branch: Optional branch to push (current branch if None)
            repo_path: Optional path to repository

        Returns:
            Push operation result
        """
        command = ["push"]
        if branch:
            command.extend(["origin", branch])

        result = await self._run_git_command(command, cwd=repo_path)

        if result["success"]:
            target = f" to {branch}" if branch else ""
            result["message"] = f"Successfully pushed changes{target}"

        return result

    async def get_log(
        self, limit: int = 10, repo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get git commit log.

        Args:
            limit: Number of commits to retrieve
            repo_path: Optional path to repository

        Returns:
            Commit log information
        """
        command = ["log", f"-{limit}", "--oneline", "--graph"]
        result = await self._run_git_command(command, cwd=repo_path)

        if result["success"]:
            commits = [
                line.strip() for line in result["output"].split("\n") if line.strip()
            ]
            result["commits"] = commits
            result["message"] = f"Retrieved {len(commits)} commits"

        return result

    def get_dependencies(self) -> List[str]:
        """Return plugin dependencies."""
        return ["command:git"]

    def shutdown(self) -> None:
        """Shutdown the plugin."""
        logger.info("Shutting down Git integration plugin")
        super().shutdown()

    def get_metadata(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        metadata = super().get_metadata()
        metadata.update(
            {
                "description": "Comprehensive Git integration for Atlas",
                "capabilities": [
                    "repository_status",
                    "commit_operations",
                    "branch_management",
                    "remote_operations",
                    "commit_history",
                ],
                "git_available": self._git_available,
                "current_repo": self.current_repo_path or "None",
            }
        )
        return metadata
