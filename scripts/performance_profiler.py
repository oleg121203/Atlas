#!/usr/bin/env python
"""
Performance Profiling Tool

This script helps identify and optimize slow operations in the Atlas application.
It uses cProfile for function-level profiling and line_profiler for line-level analysis.
"""

import cProfile
import importlib
import io
import os
import pstats
import subprocess
import sys
from datetime import datetime


def ensure_dependencies():
    """Ensure all required profiling packages are installed."""
    required_packages = ["line_profiler", "memory_profiler", "psutil"]
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"Installing required package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def run_cprofile(module_path, function_name=None):
    """Run cProfile on the specified module or function."""
    print(f"\n{'-' * 20} cProfile Analysis {'-' * 20}")

    if not os.path.exists(module_path):
        print(f"Error: Module path '{module_path}' does not exist.")
        return

    module_name = os.path.splitext(os.path.basename(module_path))[0]
    module_dir = os.path.dirname(module_path)

    # Temporarily add the module directory to sys.path
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    # Create a cProfile profiler
    pr = cProfile.Profile()

    try:
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Start profiling
        pr.enable()

        if function_name:
            # Run a specific function if provided
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                func()
            else:
                print(
                    f"Error: Function '{function_name}' not found in module '{module_name}'"
                )
                return
        else:
            # Otherwise, profile the entire module
            pass

        # Stop profiling
        pr.disable()

        # Process and display results
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats(30)  # Print top 30 time-consuming functions
        print(s.getvalue())

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"profile_results_{module_name}_{timestamp}.prof"
        with open(result_file, "w") as f:
            ps = pstats.Stats(pr, stream=f).sort_stats("cumulative")
            ps.print_stats()

        print(f"Detailed profile results saved to {result_file}")

    finally:
        # Remove the module directory from sys.path
        if module_dir in sys.path:
            sys.path.remove(module_dir)


def run_line_profiler(module_path, function_name):
    """Run line_profiler on the specified function."""
    print(f"\n{'-' * 20} Line-by-Line Profiling {'-' * 20}")

    if not os.path.exists(module_path):
        print(f"Error: Module path '{module_path}' does not exist.")
        return

    if not function_name:
        print("Error: Function name must be provided for line profiling.")
        return

    try:
        # Use the kernprof command-line tool from line_profiler
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "line_profile_wrapper.py")
        )

        # Create the wrapper script if it doesn't exist
        if not os.path.exists(script_path):
            with open(script_path, "w") as f:
                f.write('''
#!/usr/bin/env python
"""Line Profiler Wrapper"""

import sys
import os
import importlib.util

def main():
    if len(sys.argv) < 3:
        print("Usage: line_profile_wrapper.py <module_path> <function_name>")
        return

    module_path = sys.argv[1]
    function_name = sys.argv[2]

    # Add the module directory to sys.path
    module_dir = os.path.dirname(module_path)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    # Import the module
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the function to profile
    if hasattr(module, function_name):
        func = getattr(module, function_name)
        # Apply the @profile decorator
        func = globals().get("profile", lambda x: x)(func)
        # Execute the function
        func()
    else:
        print(f"Error: Function '{function_name}' not found in module '{module_name}'")

if __name__ == "__main__":
    main()
''')

        # Make the wrapper script executable
        os.chmod(script_path, 0o755)

        # Run kernprof
        cmd = ["kernprof", "-l", "-v", script_path, module_path, function_name]
        subprocess.run(cmd)

    except FileNotFoundError:
        print(
            "Error: kernprof command not found. Make sure line_profiler is properly installed."
        )
    except Exception as e:
        print(f"Error during line profiling: {e}")


def run_memory_profiler(module_path, function_name):
    """Run memory_profiler on the specified function."""
    print(f"\n{'-' * 20} Memory Profiling {'-' * 20}")

    if not os.path.exists(module_path):
        print(f"Error: Module path '{module_path}' does not exist.")
        return

    if not function_name:
        print("Error: Function name must be provided for memory profiling.")
        return

    try:
        # Use the mprof command-line tool from memory_profiler
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create a small Python script to run the function with memory_profiler
        script_content = f'''
#!/usr/bin/env python
"""Memory Profiler Runner"""

import sys
import os
import importlib.util
from memory_profiler import profile

# Add the module directory to sys.path
module_dir = os.path.dirname("{module_path}")
if module_dir and module_dir not in sys.path:
    sys.path.insert(0, module_dir)

# Import the module
module_name = "{module_name}"
spec = importlib.util.spec_from_file_location(module_name, "{module_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Get and profile the function
if hasattr(module, "{function_name}"):
    func = getattr(module, "{function_name}")
    profiled_func = profile(func)
    profiled_func()
else:
    print(f"Error: Function '{function_name}' not found in module '{module_name}'")
'''

        script_path = f"memory_profile_runner_{timestamp}.py"
        with open(script_path, "w") as f:
            f.write(script_content)

        # Run the script with memory_profiler
        cmd = [sys.executable, "-m", "memory_profiler", script_path]
        subprocess.run(cmd)

        # Clean up
        os.remove(script_path)

    except Exception as e:
        print(f"Error during memory profiling: {e}")


def main():
    """Main function to run the script."""
    print("Atlas Performance Profiling Tool")
    print("============================")

    # Ensure required packages are installed
    ensure_dependencies()

    # Get module path and function name from arguments or user input
    module_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else input("Enter the path to the Python module to profile: ")
    )

    if len(sys.argv) > 2:
        function_name = sys.argv[2]
    else:
        function_name = input(
            "Enter the function name to profile (leave empty to profile the entire module): "
        )
        if function_name.strip() == "":
            function_name = None

    # Ask which profiler to use
    print("\nSelect profiling method:")
    print("1. cProfile (function-level profiling)")
    print("2. line_profiler (line-by-line profiling)")
    print("3. memory_profiler (memory usage profiling)")
    print("4. All profilers")

    choice = input("Enter your choice (1-4): ")

    if choice == "1" or choice == "4":
        run_cprofile(module_path, function_name)

    if choice == "2" or choice == "4":
        if function_name:
            run_line_profiler(module_path, function_name)
        else:
            print("Line profiler requires a function name. Skipping line profiling.")

    if choice == "3" or choice == "4":
        if function_name:
            run_memory_profiler(module_path, function_name)
        else:
            print(
                "Memory profiler requires a function name. Skipping memory profiling."
            )

    print(
        "\nProfiling completed. Use the results to identify and optimize slow operations."
    )


if __name__ == "__main__":
    main()
