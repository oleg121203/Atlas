"""OCR utilities for Atlas.

Uses Vision framework on macOS when available, falling back to pytesseract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

# Try to import PIL safely
try:
    from PIL import Image

    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

try:
    import Vision  # type: ignore

    _VISION_AVAILABLE = True
except Exception:  # pragma: no cover
    _VISION_AVAILABLE = False

# Try to import pytesseract safely
try:
    import pytesseract  # type: ignore

    _PYTESSERACT_AVAILABLE = True
except ImportError:
    _PYTESSERACT_AVAILABLE = False

__all__ = ["ocr_file", "ocr_image"]


def _vision_ocr(img: Image.Image) -> str:
    """Perform OCR using macOS Vision framework."""

    cg_img = img.convert("RGB").toqpixmap().toImage()
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(
        cg_img, None
    )
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    error = handler.performRequests_error_([request], None)
    if error is not None:
        raise RuntimeError(error)
    observations = request.results() or []
    return "\n".join(o.string() for o in observations)


def ocr_image(img: Image.Image) -> str:
    """Return recognized text from *img* using best available backend."""
    if not _PIL_AVAILABLE:
        raise RuntimeError(
            "PIL (Pillow) is not available. Cannot perform OCR on images."
        )

    if _VISION_AVAILABLE:
        try:
            return _vision_ocr(img)
        except Exception:
            pass  # fall through

    if _PYTESSERACT_AVAILABLE:
        return pytesseract.image_to_string(img)
    raise RuntimeError("No OCR backend available (missing pytesseract and Vision)")


def ocr_file(path: Path | str, *, lang: Optional[str] = None) -> str:
    """OCR an image file at *path* and return text."""
    if not _PIL_AVAILABLE:
        raise RuntimeError(
            "PIL (Pillow) is not available. Cannot open image files for OCR."
        )

    img = Image.open(Path(path))
    if lang and _PYTESSERACT_AVAILABLE:
        return pytesseract.image_to_string(img, lang=lang)
    return ocr_image(img)
