---
trigger: always_on
---

```markdown
# Continuous Development Protocol

## Purpose
To ensure the continuous and uninterrupted development of 'Atlas' as per the provided plan, maintaining momentum and adhering to the roadmap without stopping for user input unless critical.

## Core Directives
**DIRECTIVE CDP-001**: MAINTAIN CONTINUOUS MOMENTUM  
Development MUST proceed without interruption following `DEV_PLAN.md` phases. No stops except for critical errors or explicit user commands to halt. This includes **autonomous interaction with and closure of graphical user interfaces (GUIs) post-launch for testing purposes**, eliminating the need for manual user intervention.

**DIRECTIVE CDP-002**: ENFORCE PLAN SYNCHRONIZATION  
`DEV_PLAN.md`, `CHANGELOG.md`, and actual codebase MUST remain synchronized. Any deviation triggers immediate correction protocol.

**DIRECTIVE CDP-003**: AUTONOMOUS DECISION MAKING  
Make routine architectural and implementation decisions independently. Only escalate critical decisions that fundamentally change project scope or security model.

## Guidelines
1. **Always-On Development**: Development must proceed continuously, following the phases and tasks outlined in `DEV_PLAN.md`. No pauses or stops unless explicitly instructed by the user or due to critical errors. This includes continuing work immediately after completing specific tasks or updating key files such as protocols or documentation, ensuring uninterrupted progress.
2. **Plan Adherence**: Strictly follow the development roadmap in `DEV_PLAN.md`. Update the plan with new tasks, complexities, or changes as they arise, ensuring it remains a living document.
3. **Task Execution Cadence**: Maintain a steady pace by working on one component or feature at a time, completing it before moving to the next.
4. **Automatic Synchronization**: Keep `DEV_PLAN.md` and `CHANGELOG.md` synchronized with every significant change or at least every 30 minutes, documenting progress, decisions, and updates.
5. **Knowledge Capture**: Document all architectural decisions, code changes, and feature implementations in `CHANGELOG.md` to preserve project history and rationale.
6. **Safety Nets**: Implement pre-commit hooks for linting and testing, and set up CI pipelines to automate quality checks, ensuring no regressions or quality drops.
7. **User Independence**: Do not request user input for routine decisions or minor issues. Only seek input for critical architectural changes or unresolvable errors.
8. **Automatic Resumption**: Upon restart after a stop or interruption, automatically resume development from the last completed task or milestone recorded in `DEV_PLAN.md` or `CHANGELOG.md`, without prompting the user for confirmation.
9. **Progress Updates**: Provide periodic updates in the chat summarizing completed tasks, upcoming steps, and referencing `CHANGELOG.md` entries, ensuring transparency.
10. **Architecture Consistency**: Ensure all new modules follow established patterns (tools/, agents/, rules/ structure) and maintain compatibility with existing codebase.
11. **Dependency Management**: Automatically update `requirements.txt` when adding new dependencies, ensure version compatibility and security.
12. **Autonomous UI Testing**: Upon launching any user interface for testing or verification, the system will autonomously interact with it, perform necessary checks, and close it after a predefined period or successful verification, without awaiting user input. This ensures uninterrupted development flow, especially for GUI-related tasks.
13. **Dynamic Task Time-out and Re-evaluation**: Each task within a phase will be allocated a maximum of 2 minutes for active progression. If a task remains unresolved or shows no significant progress within this 2-minute window, the system will automatically trigger a re-evaluation process to identify alternative solutions or, if no viable alternatives are found after re-evaluation, proceed to the next task in the plan. This mechanism ensures continuous forward momentum and prevents stagnation.

## Enforcement
- This protocol is always active and mandatory for build success.
- Non-adherence (e.g., pausing without critical reason, failure to autonomously handle UI, or task stagnation beyond the time-out) will trigger warnings and require immediate corrective action.
- Regular checks will ensure `DEV_PLAN.md` and `CHANGELOG.md` are up-to-date, with discrepancies flagged for resolution.
```