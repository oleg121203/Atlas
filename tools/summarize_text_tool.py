import re
from typing import Dict, Any

def summarize_text(text: str) -> Dict[str, Any]:
    """
    Summarize the input text by extracting the first 3 sentences.

    Args:
        text: The text to summarize.
    Returns:
        A dict with 'status', 'summary', and 'error' (if any).
    """
    try:
        sentences = re.split(r'(?<=[.!?]) +', text)
        summary = ' '.join(sentences[:3])
        return {"status": "success", "summary": summary}
    except Exception as e:
        return {"status": "error", "error": str(e)} 