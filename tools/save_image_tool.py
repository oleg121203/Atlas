from typing import Any, Dict

try:
    from PIL import Image
except ImportError:
    Image = None


def save_image(image, file_path: str) -> Dict[str, Any]:
    """
    Save a PIL image object to a file.

    Args:
        image: PIL.Image.Image object.
        file_path: Path to save the image.
    Returns:
        A dict with 'status', 'file_path', and 'error' (if any).
    """
    if Image is None:
        return {"status": "error", "error": "Pillow is not installed."}
    try:
        image.save(file_path)
        return {"status": "success", "file_path": file_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}
