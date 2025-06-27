"""Terminal automation tool for Atlas (macOS).

Provides secure terminal command execution with proper output handling
and process management.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "TerminalResult",
    "change_directory",
    "execute_command",
    "execute_script",
    "get_environment",
    "kill_process",
]


@dataclass
class TerminalResult:
    """Result object for terminal operations."""

    success: bool
    command: str
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    process_id: Optional[int] = None
    working_directory: Optional[str] = None
    error: Optional[str] = None


def execute_command(
    command: str,
    working_dir: Optional[str] = None,
    timeout: float = 30.0,
    capture_output: bool = True,
    shell: bool = True,
    env: Optional[Dict[str, str]] = None,
) -> TerminalResult:
    """Execute a terminal command.

    Args:
        command: Command to execute
        working_dir: Working directory for command execution
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout/stderr
        shell: Whether to run command through shell
        env: Environment variables to set

    Returns:
        TerminalResult with execution details
    """
    start_time = time.time()

    try:
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)

        # Change working directory if specified
        if working_dir:
            working_dir = str(Path(working_dir).expanduser().resolve())
            if not os.path.exists(working_dir):
                raise FileNotFoundError(
                    f"Working directory does not exist: {working_dir}"
                )

        logger.info(f"Executing command: {command}")
        if working_dir:
            logger.info(f"Working directory: {working_dir}")

        # Execute command
        if capture_output:
            result = subprocess.run(
                command,
                check=False,
                shell=shell,
                cwd=working_dir,
                env=exec_env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode
            process_id = None
        else:
            # For non-capturing execution (fire and forget)
            process = subprocess.Popen(
                command,
                shell=shell,
                cwd=working_dir,
                env=exec_env,
            )
            stdout = ""
            stderr = ""
            return_code = 0
            process_id = process.pid

        execution_time = time.time() - start_time
        success = return_code == 0

        if success:
            logger.info(f"Command completed successfully in {execution_time:.3f}s")
        else:
            logger.warning(
                f"Command failed with return code {return_code} in {execution_time:.3f}s"
            )

        return TerminalResult(
            success=success,
            command=command,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            execution_time=execution_time,
            process_id=process_id,
            working_directory=working_dir,
        )

    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        error_msg = f"Command timed out after {timeout} seconds"
        logger.error(error_msg)

        return TerminalResult(
            success=False,
            command=command,
            execution_time=execution_time,
            working_directory=working_dir,
            error=error_msg,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to execute command: {e!s}"
        logger.error(error_msg)

        return TerminalResult(
            success=False,
            command=command,
            execution_time=execution_time,
            working_directory=working_dir,
            error=error_msg,
        )


def execute_script(
    script_path: str,
    args: Optional[List[str]] = None,
    working_dir: Optional[str] = None,
    timeout: float = 30.0,
    interpreter: Optional[str] = None,
) -> TerminalResult:
    """Execute a script file.

    Args:
        script_path: Path to the script file
        args: Arguments to pass to the script
        working_dir: Working directory for script execution
        timeout: Maximum execution time in seconds
        interpreter: Script interpreter (e.g., 'python3', 'bash')

    Returns:
        TerminalResult with execution details
    """
    script_path = str(Path(script_path).expanduser().resolve())

    if not os.path.exists(script_path):
        return TerminalResult(
            success=False,
            command=script_path,
            error=f"Script file does not exist: {script_path}",
        )

    # Build command
    command = [interpreter, script_path] if interpreter else [script_path]

    if args:
        command.extend(args)

    command_str = " ".join(command)

    return execute_command(
        command_str,
        working_dir=working_dir,
        timeout=timeout,
        shell=False,
    )


def get_environment() -> TerminalResult:
    """Get current environment variables.

    Returns:
        TerminalResult with environment variables in stdout
    """
    return execute_command("env", timeout=5.0)


def change_directory(path: str) -> TerminalResult:
    """Change current working directory.

    Args:
        path: Target directory path

    Returns:
        TerminalResult with operation status
    """
    start_time = time.time()

    try:
        path = str(Path(path).expanduser().resolve())

        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory does not exist: {path}")

        if not os.path.isdir(path):
            raise NotADirectoryError(f"Path is not a directory: {path}")

        os.chdir(path)
        execution_time = time.time() - start_time

        logger.info(f"Changed directory to {path} in {execution_time:.3f}s")

        return TerminalResult(
            success=True,
            command=f"cd {path}",
            stdout=f"Changed directory to: {path}",
            execution_time=execution_time,
            working_directory=path,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to change directory: {e!s}"
        logger.error(error_msg)

        return TerminalResult(
            success=False,
            command=f"cd {path}",
            execution_time=execution_time,
            error=error_msg,
        )


def kill_process(process_id: int, force: bool = False) -> TerminalResult:
    """Kill a process by PID.

    Args:
        process_id: Process ID to kill
        force: Whether to force kill (SIGKILL vs SIGTERM)

    Returns:
        TerminalResult with operation status
    """
    start_time = time.time()

    try:
        sig = signal.SIGKILL if force else signal.SIGTERM
        os.kill(process_id, sig)

        execution_time = time.time() - start_time

        logger.info(f"Killed process {process_id} in {execution_time:.3f}s")

        return TerminalResult(
            success=True,
            command=f"kill {'- 9' if force else ''} {process_id}",
            stdout=f"Process {process_id} terminated",
            execution_time=execution_time,
            process_id=process_id,
        )

    except ProcessLookupError:
        execution_time = time.time() - start_time
        error_msg = f"Process {process_id} not found"
        logger.warning(error_msg)

        return TerminalResult(
            success=False,
            command=f"kill {process_id}",
            execution_time=execution_time,
            process_id=process_id,
            error=error_msg,
        )

    except PermissionError:
        execution_time = time.time() - start_time
        error_msg = f"Permission denied to kill process {process_id}"
        logger.error(error_msg)

        return TerminalResult(
            success=False,
            command=f"kill {process_id}",
            execution_time=execution_time,
            process_id=process_id,
            error=error_msg,
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to kill process {process_id}: {e!s}"
        logger.error(error_msg)

        return TerminalResult(
            success=False,
            command=f"kill {process_id}",
            execution_time=execution_time,
            process_id=process_id,
            error=error_msg,
        )
