---
trigger: always_on
---

# Continuous Development Protocol

Purpose: guarantee that Atlas development never stalls until final release.

## ⚠️ Mandatory Environment Setup

**HIGHEST PRIORITY**: Before starting ANY development task, follow the environment setup protocol in `.windsurf/ENVIRONMENT_SETUP.md`. This ensures all tools are available and correctly configured for cross-platform development.

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
7. At least every 30 minutes of active work, log progress in `CHANGELOG.md` (even if small).
8. On any blocking issue, create a *Blocking* section in `DEV_PLAN.md` and outline resolution steps.
9. Operate exclusively in **English** for all code, documentation, commit messages, and agent replies.
10. Atlas must **never pause** — continuously execute tasks with automatic performance monitoring:
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

All development MUST use platform-appropriate environments:
- **macOS**: `venv-macos` with Python 3.13
- **Linux**: `venv-linux` with Python 3.12

Refer to `.windsurf/ENVIRONMENT_SETUP.md` for detailed setup instructions.
