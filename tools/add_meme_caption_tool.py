from typing import Any, Dict

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None


def add_meme_caption(
    image_path: str, caption: str, output_path: str = "meme.png"
) -> Dict[str, Any]:
    """
    Overlay a caption on an image to create a meme.

    Args:
        image_path: Path to the input image.
        caption: Caption text to overlay.
        output_path: Path to save the meme image.
    Returns:
        A dict with 'status', 'output_path', and 'error' (if any).
    """
    if Image is None:
        return {"status": "error", "error": "Pillow is not installed."}
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        # Use a default font
        try:
            font = ImageFont.truetype("arial.ttf", size=int(height / 12))
        except Exception:
            font = ImageFont.load_default()
        # Calculate text size and position
        text_width, text_height = draw.textsize(caption, font=font)
        x = (width - text_width) / 2
        y = height - text_height - 20
        # Draw outline
        outline_range = 2
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                draw.text((x + dx, y + dy), caption, font=font, fill="black")
        # Draw main text
        draw.text((x, y), caption, font=font, fill="white")
        img.save(output_path)
        return {"status": "success", "output_path": output_path}
    except Exception as e:
        return {"status": "error", "error": str(e)}
