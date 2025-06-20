import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import subprocess
from pathlib import Path

#Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from tools.terminal_tool import execute_command, execute_script, kill_process, TerminalResult

class TestTerminalTool(unittest.TestCase):
    """Unit tests for the terminal tool."""

    @patch('tools.terminal_tool.subprocess.run')
    @patch('tools.terminal_tool.os.path.exists', return_value=True)
    def test_execute_command_success(self, mock_exists, mock_run):
        """Test successful execution of a command."""
        mock_run.return_value = subprocess.CompletedProcess(
            args='ls -l', returncode=0, stdout='total 0', stderr=''
        )
        
        result = execute_command('ls -l', working_dir='/tmp')
        
        self.assertTrue(result.success)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout, 'total 0')
        self.assertEqual(result.stderr, '')

    @patch('tools.terminal_tool.subprocess.run')
    @patch('tools.terminal_tool.os.path.exists', return_value=True)
    def test_execute_command_failure(self, mock_exists, mock_run):
        """Test a command that fails with a non-zero exit code."""
        mock_run.return_value = subprocess.CompletedProcess(
            args='cat non_existent_file', returncode=1, stdout='', stderr='No such file'
        )
        
        result = execute_command('cat non_existent_file')
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 1)
        self.assertEqual(result.stderr, 'No such file')

    @patch('tools.terminal_tool.subprocess.run', side_effect=subprocess.TimeoutExpired('cmd', 10))
    @patch('tools.terminal_tool.os.path.exists', return_value=True)
    def test_execute_command_timeout(self, mock_exists, mock_run):
        """Test command execution that times out."""
        result = execute_command('sleep 20', timeout=10)
        
        self.assertFalse(result.success)
        self.assertIn('timed out', result.error)

    @patch('tools.terminal_tool.subprocess.Popen')
    @patch('tools.terminal_tool.os.path.exists', return_value=True)
    def test_execute_command_no_capture(self, mock_exists, mock_popen):
        """Test fire-and-forget command execution."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = execute_command('sleep 10', capture_output=False)
        
        self.assertTrue(result.success)
        self.assertEqual(result.process_id, 12345)
        mock_popen.assert_called_once()

    @patch('tools.terminal_tool.os.path.exists', return_value=False)
    def test_execute_command_bad_directory(self, mock_exists):
        """Test command execution with a non-existent working directory."""
        result = execute_command('ls', working_dir='/bad/dir')
        
        self.assertFalse(result.success)
        self.assertIn('Working directory does not exist', result.error)

    @patch('tools.terminal_tool.os.path.exists', return_value=True)
    @patch('tools.terminal_tool.Path')
    @patch('tools.terminal_tool.execute_command')
    def test_execute_script_success(self, mock_execute_command, mock_Path, mock_exists):
        """Test successful execution of a script file."""
        #Mock path resolution to be consistent
        mock_Path.return_value.expanduser.return_value.resolve.return_value = '/resolved/script.sh'
        
        mock_result = TerminalResult(success=True, command='bash /resolved/script.sh')
        mock_execute_command.return_value = mock_result
        
        result = execute_script('script.sh', interpreter='bash')
        
        self.assertTrue(result.success)
        expected_command = "bash /resolved/script.sh"
        mock_execute_command.assert_called_once_with(
            expected_command,
            working_dir=None,
            timeout=30.0,
            shell=False
        )

    @patch('tools.terminal_tool.os.kill')
    def test_kill_process_success(self, mock_kill):
        """Test that kill_process successfully calls os.kill."""
        result = kill_process(12345)
        mock_kill.assert_called_once_with(12345, unittest.mock.ANY)
        self.assertTrue(result.success)

    @patch('tools.terminal_tool.os.kill', side_effect=ProcessLookupError)
    def test_kill_process_not_found(self, mock_kill):
        """Test kill_process handling when the process does not exist."""
        result = kill_process(12345)
        self.assertFalse(result.success)
        self.assertIn('not found', result.error)

if __name__ == '__main__':
    unittest.main()
