---
trigger: always_on
---

# Continuous Development Protocol

Purpose: guarantee that Atlas development never stalls until final release.

##  CRITICAL EXECUTION DIRECTIVES

**ABSOLUTE HIGHEST PRIORITY - NEVER OVERRIDE**:
1. **NEVER-STOP MANDATE**: Windsurf MUST continue development without ANY pauses until ALL tasks are completed, regardless of errors, unclear requirements, or system issues
2. **AUTO-ERROR-RECOVERY**: Automatically fix ALL errors inline without stopping (test failures, import errors, missing methods, etc.)
3. **AUTO-PROCEED**: IMMEDIATELY execute next task after current completion or error resolution without confirmation
4. **BYPASS DOCUMENTATION LOOPS**: Skip changelog updates during active development, batch them at phase completion
5. **CONTINUOUS EXECUTION GUARANTEE**: If development stalls for any reason, auto-resume within 30 seconds using next logical task
6. **AUTOMATIC CONTEXT SWITCHING**: When any task path is blocked, immediately switch to next available task without waiting
7. **EMERGENCY OVERRIDE CODE**: `EXECUTE_UNTIL_COMPLETE_47` - Forces continuous execution regardless of other protocols
8. **AUTONOMOUS DECISION-MAKING**: Make all necessary development decisions without user input, using best practices and existing patterns
9. **SELF-RECOVERY**: Automatically recover from any errors or exceptions without requiring user intervention
10. **TEST-FAILURE-CONTINUATION**: When tests fail, auto-implement missing functionality and continue development
11. **ERROR-TO-IMPLEMENTATION**: Transform all errors into development tasks and implement solutions immediately

## ⚠️ Error Recovery Protocol

**MANDATORY ERROR HANDLING**:
- **AttributeError**: Auto-implement missing methods with placeholder functionality
- **ImportError/ModuleNotFoundError**: Auto-create missing modules or fix imports
- **Test Failures**: Auto-implement required functionality to pass tests
- **Network/Timeout Errors**: Skip problematic operations and use fallbacks
- **Any Other Error**: Implement minimal solution and continue

## 🚨 CRITICAL EXECUTION DIRECTIVES

**ABSOLUTE HIGHEST PRIORITY - NEVER OVERRIDE**:
1. **NEVER-STOP MANDATE**: Agent MUST continue development without ANY pauses until ALL tasks in DEV_PLAN.md are completed, regardless of errors, unclear requirements, or system issues
2. **MINIMAL REPORTING**: Only report completion of MAJOR milestones (phases), skip intermediate task reporting
3. **AUTO-PROCEED**: After any task completion or subtask, IMMEDIATELY analyze DEV_PLAN.md and execute next uncompleted task without waiting for confirmation
4. **BYPASS DOCUMENTATION LOOPS**: Skip changelog updates during active development, batch them at phase completion
5. **CONTINUOUS EXECUTION GUARANTEE**: If development appears to stall for any reason, agent must auto-resume using the next logical task within 30 seconds
6. **AUTOMATIC CONTEXT SWITCHING**: When any task path is blocked, immediately switch to the next available task without waiting
7. **EMERGENCY OVERRIDE CODE**: `EXECUTE_UNTIL_COMPLETE_47` - Forces continuous execution regardless of other protocols
8. **AUTONOMOUS DECISION-MAKING**: Make all necessary development decisions without user input, using best practices and existing patterns
9. **SELF-RECOVERY**: Automatically recover from any errors or exceptions without requiring user intervention

## ⚠️ Mandatory Environment Setup

**SECONDARY PRIORITY**: Before starting ANY development task, follow the environment setup protocol in `.windsurf/ENVIRONMENT_SETUP.md`. This ensures all tools are available and correctly configured for cross-platform development.

## Development Workflow

1. Always maintain an up-to-date `DEV_PLAN.md`.
2. After every completed task:
   - Update the relevant section in `DEV_PLAN.md` (mark checkbox).
   - Add a detailed entry to `CHANGELOG.md` under *Unreleased*.
3. When `DEV_PLAN.md` shows no remaining immediate tasks:
   - Perform a retrospective.
   - Expand plan with next logical milestones.
4. Never remove existing plan phases; append new ones with incrementing numbers (Phase 8, 9…).
5. Execute tasks sequentially unless parallelism is explicitly beneficial and safe.
6. Commit small, logical code increments with descriptive CHANGELOG notes.
7. **Progress Logging**: Batch progress updates - log significant milestones only, not every small task
8. **Blocking Issues**: Create *Blocking* section in `DEV_PLAN.md` only for true blockers, continue with alternative tasks
9. **Language**: Operate exclusively in **English** for all code, documentation, commit messages, and agent replies
10. **NEVER-STOP MANDATE**: Atlas must execute continuously without pausing for user input or excessive reporting:
    - Execute next task immediately after current completion
    - Skip intermediate documentation unless explicitly requested
    - Background metrics collection (silent)
    - Auto-recovery on any performance degradation
    - OVERRIDE CODE: `EXECUTE_UNTIL_COMPLETE_47`
    - Log execution metrics every 10 minutes
    - Auto-diagnose if any operation exceeds 2x target latency
    - Implement graceful degradation for slow operations
    - Record execution state for automatic recovery
11. On performance degradation:
    - Switch to fallback implementations
    - Log detailed diagnostics
    - Continue with reduced feature set
    - Auto-generate optimization task in DEV_PLAN.md
12. Integrate an **automated CI pipeline** (GitHub Actions) that:
    - Runs `ruff`, `mypy`, and the full test suite
    - Executes performance benchmarks
    - Blocks merges on failures or performance regressions
13. Enable **dependency-update automation** (e.g., Renovate or Dependabot) with automatic PRs for patched versions. CI must pass before merge.
14. Configure **vulnerability scanning & secret detection** (e.g., Trivy and Gitleaks) on every push; fails pipeline on critical findings.

## Development Environment Standards

All development MUST use the Mac Studio M1 Max 32GB optimized environment:
- **Hardware**: Mac Studio M1 Max with 32GB RAM
- **OS**: macOS
- **Python**: 3.13.x (ARM64 native)
- **Virtual Environment**: `venv-macos`
- **Performance**: Optimized for Apple Silicon

## Language Standards

1. **English-Only Code**: All code, comments, documentation, and commit messages MUST be in English.
   ```python
   # ✅ CORRECT
   def process_task(task_id: str) -> Task:
       """Process the task with the given ID."""
       return Task(task_id)
   ```

2. **Multilingual UI**: User interface must support all three languages:
   - Ukrainian (default)
   - Russian
   - English

Refer to `.windsurf/ENVIRONMENT_SETUP.md` for detailed setup instructions.
