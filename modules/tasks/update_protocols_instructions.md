# Task: Final Protocol Perfection

The hardening summary mentions Rules 13-14 (CDP) and 12-13 (QAP), but the files still stop at 12 and 11 respectively.  Add the missing rules so the written protocols exactly match the implemented CI/security features.

---
## 1. continuous_development_protocol.md  
Path: `.windsurf/rules/continuous_development_protocol.md`

Append **after current Rule 12**:

```
13. Enable **dependency-update automation** (Renovate or Dependabot) with automatic PRs for patched versions. CI must pass before merge.
14. Configure **vulnerability scanning & secret detection** (Trivy, Gitleaks) on every push; the pipeline must fail on critical findings.
```

---
## 2. quality_assurance_protocol.md  
Path: `.windsurf/rules/quality_assurance_protocol.md`

Append **after current Rule 11** (continue numbering → 12 & 13):

```
12. **Secret Scanning**: CI step (`gitleaks`) blocks merges if any credential/API key is found.
13. **Docstring Coverage**: Maintain ≥ 85 % public-API docstring coverage (enforced via `interrogate` or `pydocstyle`).
```

---
## 3. Documentation Updates
* CHANGELOG.md → *Unreleased → Added*: “Protocol perfection: added dependency-update automation & security scanning rules.”
* DEV_PLAN.md → Governance Enhancements: mark new bullet “Protocol perfection (dependency updates & secret/vuln scans)” as **done** once committed.

---
## 4. Verification
1. Confirm numbering is sequential in both protocol files.
2. Push and ensure CI passes with the already-configured security steps.

After these edits, the written protocols will be fully aligned with the implemented tooling.
