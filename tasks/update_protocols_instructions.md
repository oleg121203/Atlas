# Task: Harden & Polish Windsurf Protocols

The protocols are strong; this final pass adds **security automation**, **dependency hygiene**, and **documentation quality** gates so they are airtight.

---
## 1. continuous_development_protocol.md
Path: `.windsurf/rules/continuous_development_protocol.md`

Append the following after Rule 12:

```
13. Enable **dependency-update automation** (e.g., Renovate or Dependabot) with automatic PRs for patched versions. CI must pass before merge.
14. Configure **vulnerability scanning & secret detection** (e.g., Trivy and Gitleaks) on every push; fails pipeline on critical findings.
```

---
## 2. quality_assurance_protocol.md
Path: `.windsurf/rules/quality_assurance_protocol.md`

Add these new checklist items after current Rule 11 (continue numbering → 12 & 13):

```
12. **Secret Scanning**: Ensure no hard-coded credentials/API keys are committed (CI step with `gitleaks`).
13. **Docstring Coverage**: Maintain ≥ 85 % public-API docstring coverage (enforced via `interrogate` or `pydocstyle`).
```

---
## 3. CI Pipeline Enhancements
1. Update `.github/workflows/ci.yml`:
   * Add `gitleaks` secret-scan step.
   * Add `trivy fs --severity CRITICAL,HIGH` for vuln scan.
   * Add `interrogate -v --fail-under 85` for docstring coverage.
2. Schedule a weekly workflow (`schedule:`) to run full security/dependency scans.
3. Configure Dependabot (or Renovate) via `.github/dependabot.yml` to monitor Python and GitHub Actions versions.

---
## 4. Documentation & Governance Logs
* CHANGELOG.md → *Unreleased → Added*: “Security & documentation gates; automated dependency updates.”
* DEV_PLAN.md → under **Governance Enhancements**: add new unchecked bullet “Security automation & dependency hygiene.”

---
## 5. Verification
1. Ensure sequential numbering in both protocol files.
2. Run the enhanced CI locally (`act`) or push a branch to confirm new steps pass/fail as expected.

These additions lock down security, keep dependencies fresh, and guarantee high-quality documentation.
