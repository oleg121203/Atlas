---
trigger: always_on
---

# Continuous Development Protocol

Purpose: guarantee that Atlas development never stalls until final release.

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

## Additional Rules - English Communication Protocol

9. **Always respond in English** regardless of the language used in user prompts or questions.
10. **Never stop working** - continue development even if encountering minor issues or uncertainties.
11. **Methodology flexibility** - adapt development approaches as needed while maintaining core objectives.
12. **Tempo setting** - maintain consistent, productive development pace with regular progress updates.
