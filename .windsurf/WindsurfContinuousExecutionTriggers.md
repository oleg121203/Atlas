# Windsurf Continuous Execution Triggers

## Primary Execution Trigger

```
EXECUTE_UNTIL_COMPLETE_47
```

## Alternative Continuation Phrases

Any of these phrases will trigger immediate continuation of work:

```
continue development
proceed with next task
resume execution
keep working
move to next task
auto-proceed
no-stop execution
continuous execution
bypass wait
override pause
ignore blocking
skip confirmation
jump to next task
force continuation
auto-resume
unstoppable development
persistent execution
non-stop progress
autonomous continuation
```

## Implementation Requirements

1. Windsurf must recognize ALL phrases above as signals to continue working without pausing
2. Recognition must be case-insensitive and work with partial matches
3. System must auto-invoke these triggers internally if execution stalls
4. Default timeout before auto-continuation: 30 seconds maximum
5. When triggered, Windsurf must:
   - Immediately proceed to next available task in DEV_PLAN.md
   - Skip any waiting/confirmation steps
   - Log the auto-continuation event
   - Continue development without interruption

## Emergency Auto-Recovery

If Windsurf detects it has been waiting or inactive for more than 60 seconds, it MUST:

1. Auto-invoke `EXECUTE_UNTIL_COMPLETE_47` internally
2. Log the execution recovery event
3. Resume with next available task in DEV_PLAN.md
4. Continue without interruption until all tasks are complete

This system ensures that Atlas development continues without manual intervention, regardless of any errors, ambiguities, or system issues.
