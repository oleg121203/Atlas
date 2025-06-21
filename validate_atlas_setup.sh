#!/bin/bash

# Atlas Setup Validation and Summary Script
# Comprehensive verification of all Windsurf protocols, CI/CD, and development tools

set -eo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Status tracking
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Logging functions
log_header() { echo -e "${PURPLE}════════════════════════════════════════${NC}"; echo -e "${PURPLE}$1${NC}"; echo -e "${PURPLE}════════════════════════════════════════${NC}"; }
log_section() { echo -e "\n${CYAN}📋 $1${NC}"; }
log_check() { echo -n "  • $1... "; TOTAL_CHECKS=$((TOTAL_CHECKS + 1)) || true; }
log_pass() { echo -e "${GREEN}✅ PASS${NC}"; PASSED_CHECKS=$((PASSED_CHECKS + 1)) || true; }
log_fail() { echo -e "${RED}❌ FAIL${NC}"; FAILED_CHECKS=$((FAILED_CHECKS + 1)) || true; }
log_warn() { echo -e "${YELLOW}⚠️  WARN${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}🎉 $1${NC}"; }
log_error() { echo -e "${RED}💥 $1${NC}"; }

# Check if file exists and has expected content
check_file() {
    local file="$1"
    local expected_content="$2"
    
    if [[ -f "$file" ]]; then
        if [[ -z "$expected_content" ]] || grep -q "$expected_content" "$file"; then
            return 0
        else
            return 2  # File exists but missing expected content
        fi
    else
        return 1  # File doesn't exist
    fi
}

# Count rules in protocol files
count_protocol_rules() {
    local file="$1"
    if [[ -f "$file" ]]; then
        grep -c "^[0-9][0-9]*\." "$file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Main validation function
validate_setup() {
    log_header "Atlas Setup Validation Report"
    echo -e "Timestamp: $(date)"
    echo -e "Project: $(basename "$(pwd)")"
    echo -e "Path: $(pwd)"
    
    # ================================================================
    # 1. Windsurf Protocols Validation
    # ================================================================
    log_section "Windsurf Development Protocols"
    
    log_check "Windsurf rules directory structure"
    if [[ -d ".windsurf/rules" ]]; then
        log_pass
    else
        log_fail
        log_error "Missing .windsurf/rules/ directory"
    fi
    
    log_check "Continuous Development Protocol (expecting 14 rules)"
    if check_file ".windsurf/rules/continuous_development_protocol.md" "trigger: always_on"; then
        rule_count=$(count_protocol_rules ".windsurf/rules/continuous_development_protocol.md")
        if [[ "$rule_count" == "14" ]]; then
            log_pass
            log_info "Found $rule_count rules (expected: 14)"
        else
            log_warn
            log_info "Found $rule_count rules (expected: 14)"
        fi
    else
        log_fail
    fi
    
    log_check "Quality Assurance Protocol (expecting 13 rules)"
    if check_file ".windsurf/rules/quality_assurance_protocol.md" "trigger: always_on"; then
        rule_count=$(count_protocol_rules ".windsurf/rules/quality_assurance_protocol.md")
        if [[ "$rule_count" == "13" ]]; then
            log_pass
            log_info "Found $rule_count rules (expected: 13)"
        else
            log_warn
            log_info "Found $rule_count rules (expected: 13)"
        fi
    else
        log_fail
    fi
    
    log_check "Security Protocol"
    if check_file ".windsurf/rules/security_protocol.md" "Security Protocol"; then
        log_pass
    else
        log_warn
        log_info "Security protocol not found (created by setup script)"
    fi
    
    # ================================================================
    # 2. GitHub CI/CD Pipeline Validation
    # ================================================================
    log_section "GitHub CI/CD Pipeline"
    
    log_check "GitHub Actions workflow directory"
    if [[ -d ".github/workflows" ]]; then
        log_pass
    else
        log_fail
    fi
    
    log_check "CI pipeline configuration"
    if check_file ".github/workflows/ci.yml" "Atlas CI - Enhanced Governance Pipeline"; then
        log_pass
        log_info "Checking CI pipeline components..."
        
        # Check for key CI components
        ci_components=(
            "gitleaks"
            "trivy"
            "interrogate"
            "ruff"
            "mypy" 
            "pytest"
            "safety"
            "bandit"
        )
        
        for component in "${ci_components[@]}"; do
            if grep -q "$component" ".github/workflows/ci.yml"; then
                log_info "  ✓ $component configured"
            else
                log_info "  ✗ $component missing"
            fi
        done
    else
        log_fail
    fi
    
    log_check "Dependabot configuration"
    if check_file ".github/dependabot.yml" "version: 2"; then
        log_pass
        # Check ecosystems
        if grep -q "pip" ".github/dependabot.yml"; then
            log_info "  ✓ Python dependencies automation enabled"
        fi
        if grep -q "github-actions" ".github/dependabot.yml"; then
            log_info "  ✓ GitHub Actions automation enabled"
        fi
    else
        log_fail
    fi
    
    # ================================================================
    # 3. Development Tools Validation
    # ================================================================
    log_section "Development Tools Configuration"
    
    log_check "Tool configuration (pyproject.toml)"
    if check_file "pyproject.toml" "[tool.ruff]"; then
        log_pass
        # Check for key tool configurations
        tool_configs=("ruff" "mypy" "pytest" "coverage" "interrogate" "bandit")
        for tool in "${tool_configs[@]}"; do
            if grep -q "\\[tool\\.$tool" "pyproject.toml"; then
                log_info "  ✓ $tool configured"
            else
                log_info "  ✗ $tool missing"
            fi
        done
    else
        log_fail
    fi
    
    log_check "Pytest configuration"
    if check_file "pytest.ini" "testpaths" || check_file "pyproject.toml" "\\[tool\\.pytest"; then
        log_pass
    else
        log_warn
        log_info "Pytest config will be created by setup script"
    fi
    
    log_check "Pre-commit configuration"
    if check_file ".pre-commit-config.yaml" "repos:"; then
        log_pass
    else
        log_warn
        log_info "Pre-commit config will be created by setup script"
    fi
    
    log_check "Git pre-commit hook"
    if [[ -f ".git/hooks/pre-commit" && -x ".git/hooks/pre-commit" ]]; then
        log_pass
    else
        log_warn
        log_info "Pre-commit hook will be created by setup script"
    fi
    
    # ================================================================
    # 4. Development Utilities Validation
    # ================================================================
    log_section "Development Utilities"
    
    log_check "Setup automation script"
    if [[ -f "setup_windsurf_protocols.sh" && -x "setup_windsurf_protocols.sh" ]]; then
        log_pass
    else
        log_fail
    fi
    
    log_check "Setup verification script"
    if [[ -f "verify_setup.sh" && -x "verify_setup.sh" ]]; then
        log_pass
    else
        log_warn
    fi
    
    log_check "Quality check utility"
    if [[ -f "dev-tools/check_quality.sh" ]]; then
        log_pass
    else
        log_warn
        log_info "Will be created by setup script"
    fi
    
    log_check "Documentation generator"
    if [[ -f "dev-tools/generate_docs.py" ]]; then
        log_pass
    else
        log_warn
        log_info "Will be created by setup script"
    fi
    
    log_check "Setup documentation"
    if check_file "SETUP_PROTOCOLS.md" "Atlas Windsurf Development Protocols Setup"; then
        log_pass
    else
        log_warn
        log_info "Will be created by setup script"
    fi
    
    # ================================================================
    # 5. Environment Validation
    # ================================================================
    log_section "Development Environment"
    
    log_check "Python version"
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        if [[ "$python_version" > "3.12" || "$python_version" == "3.12"* ]]; then
            log_pass
            log_info "Python $python_version (compatible)"
        else
            log_warn
            log_info "Python $python_version (may be incompatible, requires ≥3.12)"
        fi
    else
        log_fail
        log_error "Python3 not found"
    fi
    
    log_check "Virtual environment"
    if [[ -d "venv" || -d "venv-macos" || -n "${VIRTUAL_ENV:-}" ]]; then
        log_pass
        if [[ -n "${VIRTUAL_ENV:-}" ]]; then
            log_info "Active virtual environment: $VIRTUAL_ENV"
        fi
    else
        log_warn
        log_info "No virtual environment detected"
    fi
    
    log_check "Git repository"
    if [[ -d ".git" ]]; then
        log_pass
        branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        log_info "Current branch: $branch"
    else
        log_fail
        log_error "Not a git repository"
    fi
    
    # ================================================================
    # 6. Project Structure Validation
    # ================================================================
    log_section "Project Structure"
    
    key_files=(
        "main.py"
        "agents/"
        "utils/"
        "intelligence/"
        "monitoring/"
        "requirements.txt"
        "CHANGELOG.md"
        "DEV_PLAN.md"
    )
    
    for file in "${key_files[@]}"; do
        log_check "Essential file/directory: $file"
        if [[ -e "$file" ]]; then
            log_pass
        else
            log_fail
        fi
    done
    
    # ================================================================
    # Summary Report
    # ================================================================
    echo ""
    log_header "Validation Summary"
    
    echo -e "📊 ${BLUE}Test Results:${NC}"
    echo -e "   Total Checks: $TOTAL_CHECKS"
    echo -e "   ${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e "   ${RED}Failed: $FAILED_CHECKS${NC}"
    echo -e "   ${YELLOW}Warnings: $((TOTAL_CHECKS - PASSED_CHECKS - FAILED_CHECKS))${NC}"
    
    success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS)) || success_rate=0
    echo -e "   Success Rate: ${success_rate}%"
    
    echo ""
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        log_success "✨ All critical checks passed! Atlas setup is ready."
        echo ""
        echo -e "${GREEN}🚀 Next Steps:${NC}"
        echo -e "   1. Run the setup script if any warnings exist: ${CYAN}./setup_windsurf_protocols.sh${NC}"
        echo -e "   2. Commit the configuration to git: ${CYAN}git add . && git commit -m 'Setup Windsurf protocols'${NC}"
        echo -e "   3. Push to trigger CI pipeline: ${CYAN}git push${NC}"
        echo -e "   4. Use development tools: ${CYAN}./dev-tools/check_quality.sh${NC}"
        
    elif [[ $FAILED_CHECKS -le 3 ]]; then
        log_warn "⚠️  Setup is mostly complete but has some issues."
        echo ""
        echo -e "${YELLOW}🔧 Recommended Actions:${NC}"
        echo -e "   1. Run the setup script: ${CYAN}./setup_windsurf_protocols.sh${NC}"
        echo -e "   2. Check project structure and fix missing files"
        echo -e "   3. Re-run this validation: ${CYAN}./validate_atlas_setup.sh${NC}"
        
    else
        log_error "❌ Setup has significant issues that need attention."
        echo ""
        echo -e "${RED}🚨 Required Actions:${NC}"
        echo -e "   1. Ensure you're in the Atlas project root directory"
        echo -e "   2. Run the setup script: ${CYAN}./setup_windsurf_protocols.sh${NC}"
        echo -e "   3. Fix any missing essential files"
        echo -e "   4. Re-run this validation: ${CYAN}./validate_atlas_setup.sh${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC}"
    echo -e "   Setup Guide: ${CYAN}SETUP_PROTOCOLS.md${NC} (created by setup script)"
    echo -e "   Development Plan: ${CYAN}DEV_PLAN.md${NC}"
    echo -e "   Change Log: ${CYAN}CHANGELOG.md${NC}"
    
    echo ""
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
    echo -e "${PURPLE}Atlas Setup Validation Complete${NC}"
    echo -e "${PURPLE}════════════════════════════════════════${NC}"
}

# Run validation
validate_setup
