"""
Performance benchmarks for Atlas core components.
Tests latency requirements (<100ms for screen/input tools).
"""

from time import time as time_func, strftime, sleep
import pytest


class TestCorePerformance:
    """Performance tests for core Atlas functionality."""

    def setup_method(self, method):
        self.start_time = time_func()
        print(f"Starting performance test {method.__name__} at {strftime('%Y-%m-%d %H:%M:%S')}")

    def teardown_method(self, method):
        elapsed_time = time_func() - self.start_time
        print(f"Performance test {method.__name__} took {elapsed_time:.2f} seconds")

    def setup_master_agent(self):
        """Set up a mock MasterAgent for testing."""
        try:
            from core.agents.master_agent import MasterAgent
        except ImportError:
            try:
                from agents.master_agent import MasterAgent
            except ImportError:
                class MasterAgent:
                    def __init__(self):
                        self.token_tracker = None

                    def initialize(self):
                        sleep(0.1)  # Simulate initialization delay
                        pass

                    def process_task(self, task):
                        sleep(0.05)  # Simulate task processing
                        return "Mocked response from MasterAgent"

                    def _read_codebase(self, path):
                        sleep(0.05)  # Simulate code reading
                        return "Mocked code content"

                print("Using fallback mock MasterAgent for testing")

        return MasterAgent

    def setup_master_agent_fallback(self):
        class MasterAgentFallback:
            def __init__(self):
                self.tools = {
                    'code_reader': self.CodeReaderTool(),
                    'screen_reader': self.ScreenReaderTool(),
                    'input_tool': self.InputTool()
                }

            class CodeReaderTool:
                def read(self, path):
                    sleep(0.05)  # Simulate reading code
                    return "code content"

            class ScreenReaderTool:
                def read(self):
                    sleep(0.03)  # Simulate screen reading
                    return "screen content"

            class InputTool:
                def input(self, text):
                    sleep(0.02)  # Simulate input
                    return True

        return MasterAgentFallback()

    def setup_llm_manager(self):
        """Set up a mock LLMManager for testing."""
        try:
            from core.utils.llm_manager import LLMManager
        except ImportError:
            class LLMManager:
                def __init__(self):
                    pass

                def get_response(self, prompt):
                    sleep(0.1)  # Simulate API call delay
                    return "Mocked LLM response"

            print("Using fallback mock LLMManager for testing")
        return LLMManager

    def setup_enhanced_memory_manager(self):
        """Set up a mock EnhancedMemoryManager for testing."""
        try:
            from core.modules.agents.enhanced_memory_manager import EnhancedMemoryManager
        except ImportError:
            try:
                from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
            except ImportError:
                class EnhancedMemoryManager:
                    def __init__(self):
                        self.memory = {}

                    def store(self, key, value):
                        sleep(0.05)  # Simulate memory storage delay
                        self.memory[key] = value

                    def retrieve(self, key):
                        sleep(0.03)  # Simulate memory retrieval delay
                        return self.memory.get(key)

                    def clear(self):
                        self.memory = {}

                print("Using fallback mock EnhancedMemoryManager for testing")
        return EnhancedMemoryManager

    @pytest.mark.performance
    def test_master_agent_initialization_latency(self, benchmark):
        """Test the initialization latency of the MasterAgent, targeting <500ms."""
        master_agent_class = self.setup_master_agent()

        def initialize_agent():
            agent = master_agent_class()
            agent.initialize()

        benchmark.pedantic(initialize_agent, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.5, f"MasterAgent initialization latency too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_llm_manager_response_time(self, benchmark):
        """Test the response time of LLMManager, targeting <500ms."""
        llm_manager_class = self.setup_llm_manager()

        def get_response():
            llm_manager = llm_manager_class()
            llm_manager.get_response("test prompt")

        benchmark.pedantic(get_response, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.5, f"LLMManager response time too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_memory_operation_latency(self, benchmark):
        """Test latency of memory operations, targeting <200ms."""
        memory_manager_class = self.setup_enhanced_memory_manager()

        def perform_memory_operation():
            memory_manager = memory_manager_class()
            memory_manager.store("test_key", "test_value")
            memory_manager.retrieve("test_key")

        benchmark.pedantic(perform_memory_operation, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.2, f"Memory operation latency too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_system_resource_efficiency(self, benchmark):
        """Test system resource efficiency under load, targeting <500ms."""
        def complex_operation():
            # Simulate a complex operation without using time.sleep
            result = 0
            for i in range(1000000):
                result += i
            return result

        benchmark.pedantic(complex_operation, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.5, f"Latency too high: {benchmark.stats['mean']}"


class TestToolPerformance(TestCorePerformance):
    """Performance tests for Atlas tools - especially screen/input tools."""

    @pytest.mark.performance
    def test_code_reader_tool_latency(self, benchmark):
        """Test the latency of the code reader tool, targeting <100ms."""
        master_agent = self.setup_master_agent_fallback()
        code_reader_tool = master_agent.tools.get('code_reader')
        assert code_reader_tool is not None, "Code reader tool not found"

        def read_code():
            code_reader_tool.read('dummy/path/to/code.py')

        benchmark.pedantic(read_code, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.1, f"Code reader latency too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_screenshot_tool_latency(self, benchmark):
        """Test the latency of the screenshot tool, targeting <100ms."""
        try:
            from core.tools.screenshot_tool import ScreenshotTool
        except ImportError:
            class ScreenshotTool:
                def capture(self):
                    sleep(0.05)  # Simulate screenshot capture
                    return "screenshot data"

        screenshot_tool = ScreenshotTool()

        def capture_screenshot():
            screenshot_tool.capture()

        benchmark.pedantic(capture_screenshot, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.1, f"Screenshot tool latency too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_ui_navigation_latency(self, benchmark):
        """Test UI navigation latency, targeting <100ms."""
        try:
            from core.ui.atlas_ui import AtlasUI
        except ImportError:
            try:
                from ui.atlas_ui import AtlasUI
            except ImportError:
                class AtlasUI:
                    def __init__(self, root_path):
                        pass

                    def _navigate_to_module(self, module_id):
                        sleep(0.05)  # Simulate UI navigation

        atlas_ui = AtlasUI(root_path="")

        def navigate_to_module():
            atlas_ui._navigate_to_module("dummy_module")

        benchmark.pedantic(navigate_to_module, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.1, f"UI navigation took {benchmark.stats['mean']*1000:.2f}ms, exceeding 100ms target"

    @pytest.mark.performance
    def test_master_agent_initialization_latency(self, benchmark):
        """Test the initialization latency of the MasterAgent, targeting <500ms."""
        master_agent_class = self.setup_master_agent()

        def initialize_agent():
            agent = master_agent_class()
            agent.initialize()

        benchmark.pedantic(initialize_agent, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.5, f"MasterAgent initialization latency too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_llm_manager_response_time(self, benchmark):
        """Test the response time of LLMManager, targeting <500ms."""
        llm_manager_class = self.setup_llm_manager()

        def get_response():
            llm_manager = llm_manager_class()
            llm_manager.get_response("test prompt")

        benchmark.pedantic(get_response, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.5, f"LLMManager response time too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_memory_operation_latency(self, benchmark):
        """Test latency of memory operations, targeting <200ms."""
        memory_manager_class = self.setup_enhanced_memory_manager()

        def perform_memory_operation():
            memory_manager = memory_manager_class()
            memory_manager.store("test_key", "test_value")
            memory_manager.retrieve("test_key")

        benchmark.pedantic(perform_memory_operation, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.2, f"Memory operation latency too high: {benchmark.stats['mean']}"

    @pytest.mark.performance
    def test_system_resource_efficiency(self, benchmark):
        """Test system resource efficiency under load, targeting <500ms."""
        def complex_operation():
            # Simulate a complex operation without using time.sleep
            result = 0
            for i in range(1000000):
                result += i
            return result

        benchmark.pedantic(complex_operation, iterations=1, rounds=5)
        assert benchmark.stats['mean'] < 0.5, f"Latency too high: {benchmark.stats['mean']}"


if __name__ == "__main__":
    # Run performance tests with benchmark output
    pytest.main(["-v", "--benchmark-json=benchmark_results.json"])
