"""
Performance benchmarks for Atlas core components.
Tests latency requirements (<100ms for screen/input tools).
"""

import pytest
import time
from unittest.mock import Mock, patch


class TestCorePerformance:
    """Performance tests for core Atlas functionality."""
    
    @pytest.mark.performance
    def test_master_agent_initialization_latency(self, benchmark):
        """Test MasterAgent initialization time."""
        def setup_master_agent():
            # Mock dependencies to focus on initialization logic
            with patch('agents.master_agent.AgentManager'), \
                 patch('agents.master_agent.LLMManager'), \
                 patch('agents.master_agent.TokenTracker'), \
                 patch('intelligence.context_awareness_engine.ContextAwarenessEngine'):
                
                from agents.master_agent import MasterAgent
                return MasterAgent(
                    config_manager=Mock(),
                    agent_manager=Mock(),
                    llm_manager=Mock(),
                    memory_manager=Mock()
                )
        
        result = benchmark(setup_master_agent)
        assert result is not None
        
        # Initialization should be under 100ms
        assert benchmark.stats['mean'] < 0.1
    
    @pytest.mark.performance
    def test_llm_manager_response_time(self, benchmark):
        """Test LLM Manager response processing time."""
        def process_mock_response():
            with patch('utils.llm_manager.openai'), \
                 patch('utils.llm_manager.anthropic'), \
                 patch('utils.llm_manager.groq'):
                
                from utils.llm_manager import LLMManager
                from agents.token_tracker import TokenTracker
                
                llm_manager = LLMManager(
                    token_tracker=TokenTracker(),
                    config_manager=Mock()
                )
                
                # Mock a simple response processing
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = "Test response"
                
                return llm_manager._extract_content_from_response(mock_response, "openai")
        
        result = benchmark(process_mock_response)
        assert result == "Test response"
        
        # Response processing should be very fast
        assert benchmark.stats['mean'] < 0.01
    
    @pytest.mark.performance
    def test_memory_operation_latency(self, benchmark):
        """Test memory storage and retrieval latency."""
        def memory_operations():
            with patch('agents.enhanced_memory_manager.chromadb'):
                from agents.enhanced_memory_manager import EnhancedMemoryManager, MemoryType
                
                memory_manager = EnhancedMemoryManager()
                
                # Store a memory entry
                memory_id = memory_manager.store_memory(
                    content="Test memory content",
                    memory_type=MemoryType.TASK_EXECUTION,
                    agent_name="test_agent"
                )
                
                # Retrieve the memory
                retrieved = memory_manager.retrieve_memories(
                    query="test",
                    memory_type=MemoryType.TASK_EXECUTION,
                    limit=1
                )
                
                return len(retrieved)
        
        result = benchmark(memory_operations)
        assert result >= 0
        
        # Memory operations should be under 50ms
        assert benchmark.stats['mean'] < 0.05


class TestToolPerformance:
    """Performance tests for Atlas tools - especially screen/input tools."""
    
    @pytest.mark.performance
    def test_screenshot_tool_latency(self, benchmark):
        """Test screenshot capture latency (must be <100ms)."""
        def capture_mock_screenshot():
            with patch('tools.screenshot_tool.pyautogui') as mock_pyautogui:
                mock_pyautogui.screenshot.return_value = Mock()
                
                from tools.screenshot_tool import capture_screen
                return capture_screen()
        
        result = benchmark(capture_mock_screenshot)
        assert result is not None
        
        # Screenshot capture must be under 100ms per requirements
        assert benchmark.stats['mean'] < 0.1
    
    @pytest.mark.performance
    def test_code_reader_tool_latency(self, benchmark):
        """Test code reading tool performance."""
        def read_mock_code():
            with patch('tools.code_reader_tool.os.path.exists', return_value=True), \
                 patch('builtins.open', mock_open_read_data="# Test code\nprint('hello')\n"):
                
                from tools.code_reader_tool import CodeReaderTool
                tool = CodeReaderTool()
                return tool.read_file("test.py")
        
        def mock_open_read_data(data):
            from unittest.mock import mock_open
            return mock_open(read_data=data)
        
        result = benchmark(read_mock_code)
        assert "Test code" in result
        
        # File reading should be very fast
        assert benchmark.stats['mean'] < 0.05


if __name__ == "__main__":
    # Run performance tests with benchmark output
    pytest.main([
        __file__,
        "--benchmark-only",
        "--benchmark-json=benchmark_results.json",
        "-v"
    ])
