import base64
import io
from pathlib import Path

from PIL import Image


def image_to_data_uri(image_path: Path | str) -> str:
    """Converts an image into a smaller JPEG encoded as a base64 data URI."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")       # remove transparency (PNG to JPEG)
        img.thumbnail((1600, 1600))    # shrink large images, keeps aspect ratio

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"