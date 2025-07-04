#!/bin/bash

# Script to run all optimization and test scripts

set -e

echo "===== Atlas Optimization and Test Suite ====="
echo "This script will run all optimization steps and tests to improve the application."
echo ""

# Check if we're in the project root
if [ ! -f "requirements.txt" ] || [ ! -d "scripts" ]; then
  echo "Error: Not in project root directory."
  echo "Please run this script from the project root directory."
  exit 1
fi

# Step 1: Update packages
echo "\n===== Step 1: Update Python Packages ====="
echo "Running package updates..."
bash scripts/update_and_test.sh

# Step 2: Code quality check
echo "\n===== Step 2: Code Quality Check ====="
echo "Running code quality checks..."
python scripts/code_quality_check.py core tools utils ui plugins

# Step 3: Performance profiling
echo "\n===== Step 3: Performance Profiling ====="
echo "Analyzing performance of critical modules..."

# List of critical modules to profile
CRITICAL_MODULES=(
  "core/application.py"
  "core/module_registry.py"
  "core/plugin_system.py"
  "core/event_bus.py"
  "utils/memory_management.py"
)

for module in "${CRITICAL_MODULES[@]}"; do
  if [ -f "$module" ]; then
    echo "\nProfiling $module..."
    python scripts/performance_profiler.py "$module" ""
  else
    echo "Warning: Module $module not found, skipping."
  fi
done

# Step 4: Memory optimization
echo "\n===== Step 4: Memory Optimization ====="
echo "Optimizing memory operations..."
python scripts/optimize_memory.py core
python scripts/optimize_memory.py utils

# Step 5: Test coverage enhancement
echo "\n===== Step 5: Test Coverage Enhancement ====="
echo "Analyzing test coverage and generating test templates..."
python scripts/test_coverage_enhancer.py

# Step 6: Run tests to verify everything still works
echo "\n===== Step 6: Final Test Verification ====="
echo "Running tests to verify all optimizations..."
python scripts/run_tests.py

# Print summary
echo "\n===== Optimization Summary ====="
echo "All optimization steps have been completed."
echo "Please review the test results and fix any remaining issues."
echo "The following tasks were performed:"
echo "✓ Updated Python packages"
echo "✓ Performed code quality checks"
echo "✓ Profiled critical modules for performance bottlenecks"
echo "✓ Optimized memory operations with lazy loading and caching"
echo "✓ Generated test templates for low-coverage modules"
echo "✓ Verified all changes with the test suite"
echo ""
echo "Next steps:"
echo "1. Implement the generated test templates to improve coverage"
echo "2. Address any code quality issues found by the linters"
echo "3. Fix any remaining performance bottlenecks identified by the profiler"
echo "4. Update CHANGELOG.md with all changes made"
