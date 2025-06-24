import os
from typing import Dict, Any
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """
    Extract text from a PDF file using PyPDF2.

    Args:
        file_path: Path to the PDF file.
    Returns:
        A dict with 'status', 'text', and 'error' (if any).
    """
    if PyPDF2 is None:
        return {"status": "error", "error": "PyPDF2 is not installed."}
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return {"status": "success", "text": text}
    except Exception as e:
        return {"status": "error", "error": str(e)} 