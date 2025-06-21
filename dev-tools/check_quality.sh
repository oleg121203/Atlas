#!/bin/bash
# Atlas Quality Check Script

echo "🔍 Running Atlas Quality Checks"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED_CHECKS=()

# 1. Ruff linting
echo "1. Running Ruff linting..."
if ruff check .; then
    echo -e "${GREEN}✅ Ruff linting passed${NC}"
else
    echo -e "${RED}❌ Ruff linting failed${NC}"
    FAILED_CHECKS+=("ruff")
fi

# 2. MyPy type checking
echo "2. Running MyPy type checking..."
if mypy --ignore-missing-imports agents/ utils/ intelligence/; then
    echo -e "${GREEN}✅ MyPy type checking passed${NC}"
else
    echo -e "${YELLOW}⚠️ MyPy type checking has warnings${NC}"
fi

# 3. Docstring coverage
echo "3. Checking docstring coverage..."
if interrogate -f 85 agents/ utils/ intelligence/; then
    echo -e "${GREEN}✅ Docstring coverage meets requirements (≥85%)${NC}"
else
    echo -e "${RED}❌ Docstring coverage below threshold${NC}"
    FAILED_CHECKS+=("docstrings")
fi

# 4. Security checks
echo "4. Running security checks..."
if command -v safety &> /dev/null; then
    if safety check; then
        echo -e "${GREEN}✅ Safety check passed${NC}"
    else
        echo -e "${RED}❌ Safety check found vulnerabilities${NC}"
        FAILED_CHECKS+=("safety")
    fi
else
    echo -e "${YELLOW}⚠️ Safety not installed, skipping vulnerability check${NC}"
fi

# 5. Run tests if they exist
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo "5. Running tests..."
    if pytest tests/ -v; then
        echo -e "${GREEN}✅ Tests passed${NC}"
    else
        echo -e "${RED}❌ Tests failed${NC}"
        FAILED_CHECKS+=("tests")
    fi
else
    echo -e "${YELLOW}⚠️ No tests directory found${NC}"
fi

# Summary
echo ""
echo "📊 Quality Check Summary"
echo "========================"

if [ ${#FAILED_CHECKS[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All quality checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Failed checks: ${FAILED_CHECKS[*]}${NC}"
    echo "Please fix the issues before committing."
    exit 1
fi
