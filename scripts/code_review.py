"""
Code Review and Refactoring Script for Atlas

This script automates parts of the code review process for the Atlas project,
identifying potential issues and suggesting refactoring opportunities.
"""

import argparse
import os
import subprocess
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import json
import re

from core.logging import get_logger
from core.config import load_config

# Set up logging
logger = get_logger("AtlasCodeReview")

class CodeReviewError(Exception):
    """Custom exception for code review errors."""
    pass

class AtlasCodeReviewer:
    """Handles automated code review and refactoring suggestions for Atlas."""
    def __init__(self, environment: str, config_path: Optional[str] = None):
        """
        Initialize the code reviewer with target environment and configuration.
        
        Args:
            environment: Target environment for review (dev, staging, prod)
            config_path: Path to configuration file, if any
        """
        self.environment = environment.lower()
        self.config = load_config(config_path, environment=self.environment)
        self.app_name = self.config.get("app_name", "atlas")
        self.review_dir = Path(self.config.get("review_dir", "code_review"))
        self.report_file = self.review_dir / f"{self.app_name}_code_review_report_{self.environment}.json"
        self.setup_logging()
        logger.info("Initialized AtlasCodeReviewer for environment: %s", self.environment)
    
    def setup_logging(self) -> None:
        """Set up logging configuration for code review."""
        log_level = self.config.get("logging", {}).get("level", "INFO")
        log_file = self.config.get("logging", {}).get("file", f"{self.app_name}_review.log")
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger.info("Logging configured for code review")
    
    def check_prerequisites(self) -> bool:
        """
        Check if all prerequisites for code review are met.
        
        Returns:
            bool: True if prerequisites are met, False otherwise
        """
        logger.info("Checking code review prerequisites")
        
        # Check if required tools are installed
        required_tools = ["python", "pip", "ruff", "mypy"]
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], check=True, capture_output=True, text=True)
                logger.debug("Tool %s is installed", tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("Required tool %s is not installed or not found", tool)
                return False
        
        # Ensure review directory exists
        self.review_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("All code review prerequisites met")
        return True
    
    def run_static_analysis(self) -> Dict:
        """
        Run static analysis tools on the codebase.
        
        Returns:
            Dict: Results from static analysis tools
        """
        logger.info("Running static analysis on Atlas codebase")
        analysis_results = {
            "ruff": self.run_ruff(),
            "mypy": self.run_mypy(),
            "complexity": self.analyze_complexity()
        }
        return analysis_results
    
    def run_ruff(self) -> Dict:
        """
        Run ruff linter on the codebase.
        
        Returns:
            Dict: Ruff analysis results
        """
        logger.info("Running ruff linter")
        try:
            result = subprocess.run(["ruff", "check", ".", "--output-format=json"], 
                                  capture_output=True, text=True, cwd=Path.cwd())
            if result.returncode == 0:
                logger.info("Ruff completed successfully")
                issues = json.loads(result.stdout) if result.stdout else []
                return {"status": "success", "issues": issues, "count": len(issues)}
            else:
                logger.warning("Ruff completed with errors")
                issues = json.loads(result.stdout) if result.stdout else []
                return {"status": "error", "issues": issues, "count": len(issues), "error": result.stderr}
        except Exception as e:
            logger.error("Error running ruff: %s", str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def run_mypy(self) -> Dict:
        """
        Run mypy type checker on the codebase.
        
        Returns:
            Dict: Mypy analysis results
        """
        logger.info("Running mypy type checker")
        try:
            result = subprocess.run(["mypy", ".", "--pretty"], 
                                  capture_output=True, text=True, cwd=Path.cwd())
            if result.returncode == 0:
                logger.info("Mypy completed successfully")
                return {"status": "success", "output": result.stdout, "issue_count": 0}
            else:
                logger.warning("Mypy found type issues")
                # Extract issue count from mypy output
                issue_count = result.stdout.count("error:")
                return {"status": "issues found", "output": result.stdout, "issue_count": issue_count}
        except Exception as e:
            logger.error("Error running mypy: %s", str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def analyze_complexity(self) -> Dict:
        """
        Analyze code complexity using various metrics.
        
        Returns:
            Dict: Complexity analysis results
        """
        logger.info("Analyzing code complexity")
        try:
            # Using radon for cyclomatic complexity if available, otherwise fallback to basic analysis
            try:
                result = subprocess.run(["radon", "cc", ".", "-s", "-j"], 
                                      capture_output=True, text=True, cwd=Path.cwd())
                if result.returncode == 0:
                    complexity_data = json.loads(result.stdout) if result.stdout else {}
                    high_complexity = self.filter_high_complexity(complexity_data)
                    return {
                        "status": "success", 
                        "high_complexity_functions": high_complexity,
                        "count": len(high_complexity)
                    }
                else:
                    logger.warning("Radon complexity analysis failed")
                    return {"status": "error", "error": result.stderr}
            except FileNotFoundError:
                logger.warning("Radon not installed, falling back to basic complexity analysis")
                return self.basic_complexity_analysis()
        except Exception as e:
            logger.error("Error analyzing complexity: %s", str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def basic_complexity_analysis(self) -> Dict:
        """
        Perform a basic complexity analysis by counting lines and nested structures.
        
        Returns:
            Dict: Basic complexity analysis results
        """
        logger.info("Performing basic complexity analysis")
        high_complexity_files = []
        source_dirs = ["core", "ui", "plugins", "modules", "security", "scripts"]
        
        for src_dir in source_dirs:
            if not Path(src_dir).exists():
                continue
                
            for py_file in Path(src_dir).rglob("*.py"):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.splitlines()
                        line_count = len(lines)
                        indent_levels = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
                        max_indent = max(indent_levels, default=0)
                        
                        # Rough heuristic: files with many lines or deep nesting might be complex
                        if line_count > 500 or max_indent > 20:
                            high_complexity_files.append({
                                "file": str(py_file),
                                "line_count": line_count,
                                "max_indent": max_indent,
                                "reason": "High line count" if line_count > 500 else "Deep nesting"
                            })
                except Exception as e:
                    logger.warning("Error analyzing file %s: %s", py_file, str(e))
        
        return {
            "status": "success",
            "high_complexity_files": high_complexity_files,
            "count": len(high_complexity_files)
        }
    
    def filter_high_complexity(self, complexity_data: Dict) -> List[Dict]:
        """
        Filter functions with high cyclomatic complexity.
        
        Args:
            complexity_data: Raw complexity data from radon
        
        Returns:
            List[Dict]: List of high complexity functions
        """
        high_complexity = []
        complexity_threshold = 10  # Grade C or worse in cyclomatic complexity
        
        for filepath, data in complexity_data.items():
            if isinstance(data, list):
                for item in data:
                    if item.get("type") == "function" and item.get("complexity", 0) >= complexity_threshold:
                        high_complexity.append({
                            "file": filepath,
                            "function": item.get("name", "Unknown"),
                            "complexity": item.get("complexity", 0),
                            "line": item.get("lineno", 0)
                        })
                    elif item.get("type") == "class":
                        methods = item.get("methods", [])
                        for method in methods:
                            if method.get("complexity", 0) >= complexity_threshold:
                                high_complexity.append({
                                    "file": filepath,
                                    "function": f"{item.get('name', 'Unknown')}.{method.get('name', 'Unknown')}",
                                    "complexity": method.get("complexity", 0),
                                    "line": method.get("lineno", 0)
                                })
        
        return sorted(high_complexity, key=lambda x: x["complexity"], reverse=True)[:10]
    
    def check_code_duplication(self) -> Dict:
        """
        Check for code duplication in the codebase.
        
        Returns:
            Dict: Duplication analysis results
        """
        logger.info("Checking for code duplication")
        try:
            # Using duplication detection if available, otherwise basic check
            try:
                result = subprocess.run(["lizard", "-l", "python", "--duplication", "--csv"], 
                                      capture_output=True, text=True, cwd=Path.cwd())
                if result.returncode == 0:
                    duplicates = self.parse_lizard_duplication(result.stdout)
                    return {
                        "status": "success",
                        "duplicates": duplicates,
                        "count": len(duplicates)
                    }
                else:
                    logger.warning("Lizard duplication check failed")
                    return {"status": "error", "error": result.stderr}
            except FileNotFoundError:
                logger.warning("Lizard not installed, skipping duplication analysis")
                return {"status": "skipped", "reason": "Lizard not installed"}
        except Exception as e:
            logger.error("Error checking code duplication: %s", str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def parse_lizard_duplication(self, output: str) -> List[Dict]:
        """
        Parse lizard duplication output.
        
        Args:
            output: Raw output from lizard tool
        
        Returns:
            List[Dict]: List of duplicated code blocks
        """
        duplicates = []
        lines = output.splitlines()
        for line in lines:
            if ",duplicate of," in line:
                parts = line.split(",")
                if len(parts) >= 5:
                    try:
                        file1 = parts[1]
                        line1 = int(parts[2])
                        file2 = parts[3]
                        line2 = int(parts[4])
                        duplicates.append({
                            "file1": file1,
                            "line1": line1,
                            "file2": file2,
                            "line2": line2
                        })
                    except (ValueError, IndexError):
                        logger.warning("Could not parse duplication line: %s", line)
        return duplicates[:10]  # Limit to top 10 duplicates
    
    def check_documentation(self) -> Dict:
        """
        Check for code documentation coverage.
        
        Returns:
            Dict: Documentation analysis results
        """
        logger.info("Checking documentation coverage")
        try:
            # Check if interrogate is installed for docstring coverage
            try:
                result = subprocess.run(["interrogate", ".", "-vv", "--json"], 
                                      capture_output=True, text=True, cwd=Path.cwd())
                if result.returncode == 0 and result.stdout:
                    doc_data = json.loads(result.stdout) if result.stdout else {}
                    return {
                        "status": "success",
                        "coverage": doc_data.get("results", {}).get("percent", 0),
                        "missing_docs": doc_data.get("results", {}).get("missing_count", 0),
                        "total": doc_data.get("results", {}).get("total_count", 0)
                    }
                else:
                    logger.warning("Interrogate documentation check failed")
                    return {"status": "error", "error": result.stderr if result.stderr else "Unknown error"}
            except FileNotFoundError:
                logger.warning("Interrogate not installed, performing basic documentation check")
                return self.basic_documentation_check()
        except Exception as e:
            logger.error("Error checking documentation: %s", str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def basic_documentation_check(self) -> Dict:
        """
        Perform a basic check for documentation in code files.
        
        Returns:
            Dict: Basic documentation check results
        """
        logger.info("Performing basic documentation check")
        source_dirs = ["core", "ui", "plugins", "modules", "security", "scripts"]
        files_without_docstrings = []
        total_files = 0
        
        for src_dir in source_dirs:
            if not Path(src_dir).exists():
                continue
                
            for py_file in Path(src_dir).rglob("*.py"):
                total_files += 1
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "def " in content or "class " in content:
                            if '"""' not in content and "'''" not in content:
                                files_without_docstrings.append(str(py_file))
                except Exception as e:
                    logger.warning("Error checking documentation in file %s: %s", py_file, str(e))
        
        coverage = 100.0 * (total_files - len(files_without_docstrings)) / total_files if total_files > 0 else 0
        return {
            "status": "success",
            "coverage": round(coverage, 2),
            "missing_docs": len(files_without_docstrings),
            "total": total_files,
            "files_without_docstrings": files_without_docstrings[:10]  # Limit to first 10
        }
    
    def check_test_coverage(self) -> Dict:
        """
        Check test coverage for the codebase.
        
        Returns:
            Dict: Test coverage results
        """
        logger.info("Checking test coverage")
        try:
            # Run pytest with coverage if available
            try:
                result = subprocess.run(["pytest", "--cov=.", "--cov-report=json"], 
                                      capture_output=True, text=True, cwd=Path.cwd())
                if result.returncode == 0 or "coverage" in result.stdout.lower():
                    # Extract coverage data from stdout or file if json report is created
                    coverage_data = {}
                    json_report_file = Path("coverage.json")
                    if json_report_file.exists():
                        with open(json_report_file, "r") as f:
                            coverage_data = json.load(f)
                            total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                            return {
                                "status": "success",
                                "coverage_percent": total_coverage,
                                "uncovered_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                                "total_lines": coverage_data.get("totals", {}).get("num_statements", 0)
                            }
                    else:
                        # Try to parse from stdout (simplified, might need adjustment based on actual output)
                        for line in result.stdout.splitlines():
                            if "TOTAL" in line and "%" in line:
                                parts = line.split()
                                for part in parts:
                                    if "%" in part:
                                        try:
                                            coverage = float(part.rstrip("%"))
                                            return {
                                                "status": "success",
                                                "coverage_percent": coverage
                                            }
                                        except ValueError:
                                            pass
                        return {"status": "error", "error": "Could not parse coverage data"}
                else:
                    logger.warning("Pytest coverage check failed")
                    return {"status": "error", "error": result.stderr}
            except FileNotFoundError:
                logger.warning("Pytest not installed, skipping test coverage check")
                return {"status": "skipped", "reason": "Pytest not installed"}
        except Exception as e:
            logger.error("Error checking test coverage: %s", str(e), exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def generate_recommendations(self, static_analysis: Dict, duplication: Dict, 
                               documentation: Dict, test_coverage: Dict) -> List[str]:
        """
        Generate refactoring recommendations based on review findings.
        
        Args:
            static_analysis: Results from static analysis tools
            duplication: Results from duplication check
            documentation: Results from documentation check
            test_coverage: Results from test coverage analysis
        
        Returns:
            List[str]: List of refactoring recommendations
        """
        logger.info("Generating refactoring recommendations")
        recommendations = []
        
        # Static analysis recommendations
        ruff_issues = static_analysis.get("ruff", {}).get("count", 0)
        if ruff_issues > 0:
            recommendations.append(f"Address {ruff_issues} issues reported by ruff linter to improve code style and quality.")
        
        mypy_issues = static_analysis.get("mypy", {}).get("issue_count", 0)
        if mypy_issues > 0:
            recommendations.append(f"Fix {mypy_issues} type issues identified by mypy to improve code reliability.")
        
        complex_funcs = static_analysis.get("complexity", {}).get("count", 0)
        if complex_funcs > 0:
            recommendations.append(f"Refactor {complex_funcs} functions/classes with high cyclomatic complexity to improve maintainability.")
        
        # Duplication recommendations
        duplicates = duplication.get("count", 0)
        if duplicates > 0:
            recommendations.append(f"Eliminate {duplicates} instances of code duplication to reduce maintenance overhead.")
        
        # Documentation recommendations
        doc_coverage = documentation.get("coverage", 0)
        if doc_coverage < 85:
            recommendations.append(f"Improve documentation coverage (currently {doc_coverage}%) to at least 85% for better code understanding.")
        
        # Test coverage recommendations
        test_cov = test_coverage.get("coverage_percent", 0)
        if test_cov > 0 and test_cov < 90:
            recommendations.append(f"Increase test coverage (currently {test_cov}%) to at least 90% to ensure code reliability.")
        elif test_cov == 0 and test_coverage.get("status") != "skipped":
            recommendations.append("Set up test coverage reporting to ensure code quality and reliability.")
        
        # General recommendations if no specific issues are found
        if not recommendations:
            recommendations.append("No critical issues found. Consider minor improvements and continue maintaining code quality.")
        
        return recommendations
    
    def generate_report(self, static_analysis: Dict, duplication: Dict, 
                       documentation: Dict, test_coverage: Dict) -> None:
        """
        Generate a comprehensive code review report.
        
        Args:
            static_analysis: Results from static analysis tools
            duplication: Results from duplication check
            documentation: Results from documentation check
            test_coverage: Results from test coverage analysis
        """
        logger.info("Generating code review report")
        import time
        report = {
            "environment": self.environment,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "static_analysis": static_analysis,
            "duplication": duplication,
            "documentation": documentation,
            "test_coverage": test_coverage,
            "recommendations": self.generate_recommendations(static_analysis, duplication, 
                                                          documentation, test_coverage)
        }
        
        with open(self.report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("Code review report generated: %s", self.report_file)
    
    def run(self) -> bool:
        """
        Execute the full code review pipeline.
        
        Returns:
            bool: True if review completed successfully, False otherwise
        """
        logger.info("Starting code review for Atlas in environment: %s", self.environment)
        try:
            if not self.check_prerequisites():
                logger.error("Code review prerequisites not met, aborting")
                return False
            
            static_analysis_results = self.run_static_analysis()
            duplication_results = self.check_code_duplication()
            documentation_results = self.check_documentation()
            test_coverage_results = self.check_test_coverage()
            
            self.generate_report(static_analysis_results, duplication_results, 
                               documentation_results, test_coverage_results)
            
            logger.info("Code review completed successfully for environment: %s", self.environment)
            return True
        except Exception as e:
            logger.error("Code review failed: %s", str(e), exc_info=True)
            return False

def main():
    """Main function to run the code review script."""
    parser = argparse.ArgumentParser(description="Code review script for Atlas")
    parser.add_argument("--environment", "-e", default="dev",
                        choices=["dev", "staging", "prod"],
                        help="Target environment for review")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    
    args = parser.parse_args()
    
    # Override log level if specified
    if args.log_level:
        logger.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))
    
    reviewer = AtlasCodeReviewer(environment=args.environment, config_path=args.config)
    success = reviewer.run()
    
    if success:
        logger.info("Code review completed successfully")
        sys.exit(0)
    else:
        logger.error("Code review failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
