#!/usr/bin/env python3
"""
Improved Atlas Code Fixer
Addresses hanging issues and provides better progress feedback.
"""

import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("ImprovedAtlasCodeFixer")

# Processing limits to prevent hanging
MAX_FILES_PER_BATCH = 10
MAX_TOTAL_FILES = 50
PROCESSING_TIMEOUT = 300  # 5 minutes max processing time
PROGRESS_UPDATE_INTERVAL = 5  # Update progress every 5 files


def check_ruff_available() -> bool:
    """Check if ruff is available."""
    try:
        result = subprocess.run(
            ["ruff", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            logger.info(f"✅ Ruff is available: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Ruff is not working correctly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.error("❌ Ruff is not installed or not accessible")
        return False


def find_python_files(max_files: int = MAX_TOTAL_FILES) -> List[str]:
    """Find Python files in the project, limited to prevent hanging."""
    logger.info(f"🔍 Searching for Python files (max {max_files})...")

    python_files = []

    # Priority directories (process these first)
    priority_dirs = ["core", "ui", "tools", "performance"]

    # Search priority directories first
    for priority_dir in priority_dirs:
        if len(python_files) >= max_files:
            break

        priority_path = Path(priority_dir)
        if priority_path.exists():
            for file_path in priority_path.rglob("*.py"):
                if len(python_files) >= max_files:
                    break
                python_files.append(str(file_path))

    # Fill remaining slots with other files if needed
    if len(python_files) < max_files:
        remaining_slots = max_files - len(python_files)
        other_files = []

        for file_path in Path(".").rglob("*.py"):
            if str(file_path) not in python_files:
                other_files.append(str(file_path))
                if len(other_files) >= remaining_slots:
                    break

        python_files.extend(other_files)

    logger.info(f"📁 Found {len(python_files)} Python files to process")
    return python_files


def run_ruff_check_with_timeout(file_path: str, timeout: int = 30) -> Tuple[bool, str]:
    """Run ruff check on a file with timeout protection."""
    try:
        result = subprocess.run(
            ["ruff", "check", "--select=F821,F401,F811,E402", file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return True, result.stdout
    except subprocess.TimeoutExpired:
        logger.warning(f"⏰ Timeout checking {file_path}")
        return False, ""
    except Exception as e:
        logger.warning(f"❌ Error checking {file_path}: {e}")
        return False, ""


def fix_simple_import_issues(file_path: str) -> int:
    """Fix simple import-related issues in a file."""
    fixes_applied = 0

    try:
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix unused imports (simple case)
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            # Skip obvious unused imports
            if (
                line.strip().startswith("import ") or line.strip().startswith("from ")
            ) and ("# noqa" not in line and "# type: ignore" not in line):
                # Simple heuristic: if import is at top level and not used later
                import_name = extract_import_name(line)
                if import_name and import_name not in content.replace(line, ""):
                    logger.debug(f"Removing unused import: {line.strip()}")
                    fixes_applied += 1
                    continue

            new_lines.append(line)

        # Write back if changes were made
        if fixes_applied > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))

        return fixes_applied

    except Exception as e:
        logger.warning(f"Error fixing {file_path}: {e}")
        return 0


def extract_import_name(import_line: str) -> str:
    """Extract the main imported name from an import line."""
    try:
        if import_line.strip().startswith("import "):
            # import module
            match = re.search(r"import\s+([a-zA-Z_][a-zA-Z0-9_]*)", import_line)
            return match.group(1) if match else ""
        elif import_line.strip().startswith("from "):
            # from module import name
            match = re.search(
                r"from\s+[\w.]+\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*)", import_line
            )
            return match.group(1) if match else ""
    except Exception:
        pass
    return ""


def process_files_safely(file_paths: List[str]) -> Tuple[int, List[str]]:
    """Process files with progress tracking and timeout protection."""
    logger.info(f"🛠️  Processing {len(file_paths)} files...")

    total_fixes = 0
    processed_files = []
    start_time = time.time()

    for i, file_path in enumerate(file_paths):
        # Check timeout
        if time.time() - start_time > PROCESSING_TIMEOUT:
            logger.warning(f"⏰ Processing timeout reached after {PROCESSING_TIMEOUT}s")
            break

        # Progress update
        if i % PROGRESS_UPDATE_INTERVAL == 0:
            logger.info(f"📊 Progress: {i + 1}/{len(file_paths)} files")

        # Skip problematic files
        if (
            not Path(file_path).exists() or Path(file_path).stat().st_size > 1_000_000
        ):  # Skip files > 1MB
            continue

        # Check file with timeout
        success, ruff_output = run_ruff_check_with_timeout(file_path)

        if success and ruff_output:
            # File has issues, try to fix them
            fixes = fix_simple_import_issues(file_path)
            if fixes > 0:
                total_fixes += fixes
                processed_files.append(file_path)
                logger.info(f"✅ Fixed {fixes} issues in {file_path}")

    logger.info(
        f"🎉 Processing complete: {total_fixes} fixes applied to {len(processed_files)} files"
    )
    return total_fixes, processed_files


def run_ruff_format_safely() -> bool:
    """Run ruff format on the entire project safely."""
    logger.info("🎨 Formatting code with ruff...")
    try:
        result = subprocess.run(
            ["ruff", "format", "."],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for formatting
        )
        if result.returncode == 0:
            logger.info("✅ Code formatting completed")
            return True
        else:
            logger.warning(f"⚠️  Formatting had issues: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Formatting timeout")
        return False
    except Exception as e:
        logger.error(f"❌ Formatting error: {e}")
        return False


def main():
    """Main function with improved error handling and progress tracking."""
    logger.info("🚀 Improved Atlas Code Fixer")
    logger.info("=" * 50)

    # Validate environment
    if not Path("pyproject.toml").exists():
        logger.error("❌ Not in Atlas project root")
        sys.exit(1)

    if not check_ruff_available():
        logger.error("❌ Ruff is not available")
        sys.exit(1)

    start_time = time.time()

    try:
        # Step 1: Find files to process
        python_files = find_python_files()

        if not python_files:
            logger.info("ℹ️  No Python files found to process")
            return

        # Step 2: Process files in batches
        total_fixes, processed_files = process_files_safely(python_files)

        # Step 3: Format code
        if total_fixes > 0:
            run_ruff_format_safely()

        # Summary
        elapsed_time = time.time() - start_time
        logger.info("\n" + "=" * 50)
        logger.info("📊 SUMMARY")
        logger.info(f"   Files processed: {len(processed_files)}")
        logger.info(f"   Fixes applied: {total_fixes}")
        logger.info(f"   Time elapsed: {elapsed_time:.1f}s")
        logger.info("=" * 50)

        if total_fixes > 0:
            logger.info("✅ Code improvements applied successfully!")
        else:
            logger.info("ℹ️  No issues found to fix")

    except KeyboardInterrupt:
        logger.info("\n⏹️  Process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
