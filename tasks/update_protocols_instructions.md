# Task: Further Refine Windsurf Protocols

The core English-only and never-stop rules are in place. Let’s elevate governance and QA to **best-in-class** by adding automation, coverage, and review cadence.

---
## 1. continuous_development_protocol.md
Path: `.windsurf/rules/continuous_development_protocol.md`

Append these items after the current last rule (10):

```
11. Establish a **weekly protocol retrospective** every Friday. Summarise learnings, adjust rules, and append concise guidance phrases that set coding tempo for the next week.
12. Integrate an **automated CI pipeline** (GitHub Actions) that runs `ruff`, `mypy`, and the full test suite on every push. Block merges on failures.
```

---
## 2. quality_assurance_protocol.md
Path: `.windsurf/rules/quality_assurance_protocol.md`

Add the following new checklist items (continue numbering; will become 10 and 11):

```
10. **Code Coverage**: Maintain ≥ 90 % statement coverage across tests. Failing the threshold blocks CI.
11. **Performance Regression**: Add automated benchmarks; flag any tool or function whose latency regresses by >10 % versus the latest main branch.
```

---
## 3. Repository Automation
1. Create `.github/workflows/ci.yml` that installs dependencies, runs `ruff`, `mypy`, `pytest --cov`, and uploads coverage report.
2. Configure `ruff` and `mypy` in `pyproject.toml` (or dedicated config files) if not present.

---
## 4. Documentation Updates
* CHANGELOG.md → *Unreleased → Added*: “Enhanced governance: added weekly retrospectives, CI enforcement, coverage & performance gates.”
* DEV_PLAN.md → under **Governance Enhancements**: add a new unchecked bullet “Automated CI & coverage/performance enforcement.”

---
## 5. Verification
1. Validate that numbering in each protocol remains sequential.
2. Push and ensure the new CI workflow runs successfully.

Completing these steps makes the protocols self-enforcing and future-proof.
