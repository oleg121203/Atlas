from collections import Counter
from typing import Any, Dict, List


def macro_suggestion(recent_actions: List[str]) -> Dict[str, Any]:
    """
    Analyze recent user actions and suggest a macro (sequence of steps) for automation.

    Args:
        recent_actions: List of recent action strings (e.g., app launches, file opens).
    Returns:
        A dict with 'status', 'macro' (list of steps), 'explanation', and 'error' (if any).
    """
    try:
        if not recent_actions:
            return {"status": "error", "error": "No recent actions provided."}
        # Find the most common consecutive sequence of 2-3 actions
        n = len(recent_actions)
        patterns = []
        for size in [3, 2]:
            for i in range(n - size + 1):
                patterns.append(tuple(recent_actions[i : i + size]))
        if not patterns:
            return {
                "status": "error",
                "error": "Not enough actions for pattern analysis.",
            }
        most_common = Counter(patterns).most_common(1)
        if not most_common or most_common[0][1] < 2:
            return {"status": "error", "error": "No repeated macro pattern found."}
        macro = list(most_common[0][0])
        explanation = (
            f"Suggested macro: {' → '.join(macro)} (repeated {most_common[0][1]} times)"
        )
        return {"status": "success", "macro": macro, "explanation": explanation}
    except Exception as e:
        return {"status": "error", "error": str(e)}
