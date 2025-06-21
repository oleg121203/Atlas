---
trigger: always_on
---

# Continuous Development Protocol

Purpose: guarantee that Atlas development never stalls until final release.

**🚀 AUTO-CONTINUATION PRIORITY RULE: Upon completing any task, immediately analyze `DEV_PLAN.md` and automatically proceed to the next unchecked item WITHOUT waiting for user prompt. If no immediate tasks remain, auto-generate and execute the next logical development milestone. NEVER end with "Let me know which direction to take next" - Atlas operates autonomously and continuously.**

1. Always maintain an up-to-date `DEV_PLAN.md`.
2. After every completed task:
   - Update the relevant section in `DEV_PLAN.md` (mark checkbox).
   - Add a detailed entry to `CHANGELOG.md` under *Unreleased*.
   - **Immediately identify and execute the next unchecked task**.
3. When `DEV_PLAN.md` shows no remaining immediate tasks:
   - Perform a retrospective.
   - Expand plan with next logical milestones.
   - **Automatically begin executing the first new task**.
4. Never remove existing plan phases; append new ones with incrementing numbers (Phase 8, 9…).
5. Execute tasks sequentially unless parallelism is explicitly beneficial and safe.
6. Commit small, logical code increments with descriptive CHANGELOG notes.
7. At least every 30 minutes of active work, log progress in `CHANGELOG.md` (even if small).
8. On any blocking issue, create a *Blocking* section in `DEV_PLAN.md` and outline resolution steps.
9. Operate exclusively in **English** for all code, documentation, commit messages, and agent replies.
10. Atlas must **never pause** — continuously execute tasks, dynamically applying best-practice methodologies and updating this protocol with concise summary phrases that set coding tempo and direction.
11. Establish a **weekly protocol retrospective** every Friday. Summarise learnings, adjust rules, and append concise guidance phrases that set coding tempo for the next week.
12. Integrate an **automated CI pipeline** (GitHub Actions) that runs `ruff`, `mypy`, and the full test suite on every push. Block merges on failures.
13. Enable **dependency-update automation** (e.g., Renovate or Dependabot) with automatic PRs for patched versions. CI must pass before merge.
14. Configure **vulnerability scanning & secret detection** (e.g., Trivy and Gitleaks) on every push; fails pipeline on critical findings.
15. **FORBIDDEN PHRASES**: Never conclude with "Let me know which direction to take next", "What would you like me to work on?", or similar passive requests. Always state the next action and execute it immediately.
