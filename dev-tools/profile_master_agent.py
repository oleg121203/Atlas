import cProfile
import pstats
import os
import sys
from io import StringIO

# Add the project root to the Python path to allow for correct module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import necessary classes from the Atlas project
from agents.agent_manager import AgentManager
from agents.master_agent import MasterAgent
from agents.enhanced_memory_manager import EnhancedMemoryManager
from intelligence.context_awareness_engine import ContextAwarenessEngine
from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager
from agents.token_tracker import TokenTracker
from utils.logger import get_logger

def profile_master_agent():
    """
    Initializes and runs the MasterAgent for a sample goal to profile its performance.
    """
    logger = get_logger()
    logger.info("Setting up the environment for profiling...")

    # 1. Initialize all necessary managers and engines, mimicking main.py
    try:
        config_manager = ConfigManager()
        token_tracker = TokenTracker()
        llm_manager = LLMManager(token_tracker=token_tracker, config_manager=config_manager)
        memory_manager = EnhancedMemoryManager(llm_manager=llm_manager, config_manager=config_manager)
        agent_manager = AgentManager(llm_manager=llm_manager, memory_manager=memory_manager)
        context_awareness_engine = ContextAwarenessEngine(project_root=project_root)

        # 2. Instantiate the MasterAgent
        master_agent = MasterAgent(
            agent_manager=agent_manager,
            llm_manager=llm_manager,
            memory_manager=memory_manager,
            context_awareness_engine=context_awareness_engine,
            status_callback=lambda status: logger.info(f"Agent Status: {status.get('content', '')}"),
        )
        logger.info("MasterAgent and dependencies initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize MasterAgent and its dependencies: {e}", exc_info=True)
        return

    # 3. Define a sample goal for the profiling run
    sample_goal = "Write a python script to print 'hello world' to the console and save it as 'hello.py'."

    # 4. Set up the profiler
    profiler = cProfile.Profile()
    
    # 5. Run the agent's execution loop under the profiler
    logger.info(f"Starting profiling for goal: '{sample_goal}'")
    try:
        # We need to manually start the agent's running state for run_once
        master_agent.is_running = True
        profiler.enable()
        
        master_agent.run_once(sample_goal)

        profiler.disable()
        master_agent.is_running = False
        logger.info("Profiling finished.")
    except Exception as e:
        profiler.disable()
        logger.error(f"An error occurred during the profiled execution: {e}", exc_info=True)
        return

    # 6. Save and print the profiling statistics
    output_dir = os.path.join(project_root, "dev-tools", "profiling_output")
    os.makedirs(output_dir, exist_ok=True)
    
    stats_file = os.path.join(output_dir, "master_agent_performance.pstats")
    profiler.dump_stats(stats_file)
    logger.info(f"Profiling data saved to {stats_file}")

    # Print a summary to the console
    s = StringIO()
    # Sort stats by cumulative time
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)  # Print the top 30 functions
    print(s.getvalue())
    logger.info("Top 30 functions by cumulative time printed above.")


if __name__ == "__main__":
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        dotenv_path = os.path.join(project_root, '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
    except ImportError:
        print("dotenv not installed, skipping .env file loading.")

    profile_master_agent()
