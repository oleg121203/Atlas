import pstats
import sys

def analyze_profile(stats_file, num_stats=30):
    """
    Analyzes a cProfile stats file and prints the top functions by cumulative time.

    Args:
        stats_file (str): The path to the .pstats file.
        num_stats (int): The number of top stats to print.
    """
    try:
        stats = pstats.Stats(stats_file)
        print(f"Analyzing profiling data from: {stats_file}\n")
        
        print(f"--- Top {num_stats} functions by cumulative time ---")
        stats.sort_stats('cumulative').print_stats(num_stats)
        
        print(f"\n--- Top {num_stats} functions by total time (exclusive of sub-calls) ---")
        stats.sort_stats('tottime').print_stats(num_stats)

    except FileNotFoundError:
        print(f"Error: The file '{stats_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        profile_file = sys.argv[1]
    else:
        profile_file = "master_agent_profile.pstats"
        print(f"No profile file specified. Defaulting to '{profile_file}'.")
        
    analyze_profile(profile_file)
