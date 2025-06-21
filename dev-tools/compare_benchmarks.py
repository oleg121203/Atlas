#!/usr/bin/env python3
"""
Performance benchmark comparison tool for Atlas CI pipeline.
Compares current branch performance against main branch baseline.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_benchmark_json(filepath: str) -> Dict[str, Any]:
    """Load benchmark results from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Benchmark file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing benchmark JSON {filepath}: {e}")
        return {}


def extract_benchmark_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """Extract relevant performance metrics from benchmark data."""
    metrics = {}
    
    if 'benchmarks' not in data:
        return metrics
    
    for benchmark in data['benchmarks']:
        name = benchmark.get('name', 'unknown')
        stats = benchmark.get('stats', {})
        
        # Get mean execution time (primary metric)
        mean_time = stats.get('mean', 0)
        if mean_time > 0:
            metrics[name] = mean_time
    
    return metrics


def compare_benchmarks(baseline: Dict[str, float], current: Dict[str, float], 
                      threshold: float = 0.10) -> Tuple[List[str], List[str], List[str]]:
    """
    Compare current benchmarks against baseline.
    
    Args:
        baseline: Baseline benchmark metrics (main branch)
        current: Current benchmark metrics (PR branch)
        threshold: Regression threshold (10% = 0.10)
    
    Returns:
        Tuple of (regressions, improvements, new_tests)
    """
    regressions = []
    improvements = []
    new_tests = []
    
    # Check for regressions and improvements
    for test_name, current_time in current.items():
        if test_name in baseline:
            baseline_time = baseline[test_name]
            if baseline_time > 0:
                change_percent = (current_time - baseline_time) / baseline_time
                
                if change_percent > threshold:
                    regressions.append(
                        f"  📈 {test_name}: {baseline_time:.4f}s → {current_time:.4f}s "
                        f"({change_percent:+.1%})"
                    )
                elif change_percent < -0.05:  # 5% improvement threshold
                    improvements.append(
                        f"  📉 {test_name}: {baseline_time:.4f}s → {current_time:.4f}s "
                        f"({change_percent:+.1%})"
                    )
        else:
            new_tests.append(f"  ✨ {test_name}: {current_time:.4f}s (new)")
    
    return regressions, improvements, new_tests


def main():
    """Main benchmark comparison function."""
    if len(sys.argv) != 3:
        print("Usage: python compare_benchmarks.py <baseline.json> <current.json>")
        sys.exit(1)
    
    baseline_file = sys.argv[1]
    current_file = sys.argv[2]
    
    print("🔍 Analyzing performance benchmarks...")
    print(f"   Baseline: {baseline_file}")
    print(f"   Current:  {current_file}")
    print()
    
    # Load benchmark data
    baseline_data = load_benchmark_json(baseline_file)
    current_data = load_benchmark_json(current_file)
    
    if not baseline_data and not current_data:
        print("⚠️  No benchmark data found. Skipping performance analysis.")
        return
    
    # Extract metrics
    baseline_metrics = extract_benchmark_metrics(baseline_data)
    current_metrics = extract_benchmark_metrics(current_data)
    
    if not baseline_metrics and not current_metrics:
        print("⚠️  No benchmark metrics found. Skipping performance analysis.")
        return
    
    print(f"📊 Found {len(baseline_metrics)} baseline tests, {len(current_metrics)} current tests")
    print()
    
    # Compare benchmarks
    regressions, improvements, new_tests = compare_benchmarks(
        baseline_metrics, current_metrics, threshold=0.10
    )
    
    # Report results
    has_issues = False
    
    if regressions:
        print("❌ PERFORMANCE REGRESSIONS DETECTED:")
        for regression in regressions:
            print(regression)
        print()
        has_issues = True
    
    if improvements:
        print("✅ Performance improvements:")
        for improvement in improvements:
            print(improvement)
        print()
    
    if new_tests:
        print("➕ New performance tests:")
        for new_test in new_tests:
            print(new_test)
        print()
    
    # Summary
    if has_issues:
        print("🚨 PERFORMANCE REGRESSION CHECK FAILED")
        print("   Performance regressions >10% detected. Please investigate.")
        sys.exit(1)
    else:
        print("✅ PERFORMANCE REGRESSION CHECK PASSED")
        print("   No significant performance regressions detected.")


if __name__ == "__main__":
    main()
