from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


def apply_food_style(image_path: str) -> str:
    source = Path(image_path)

    if not source.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    styled_path = source.parent / f"styled_{source.stem}.png"

    with Image.open(source) as img:
        img = img.convert("RGB")
        img = ImageEnhance.Brightness(img).enhance(1.04)
        img = ImageEnhance.Contrast(img).enhance(1.08)
        img = ImageEnhance.Color(img).enhance(1.10)
        img = ImageEnhance.Sharpness(img).enhance(1.10)
        img = img.filter(ImageFilter.DETAIL)
        img.save(styled_path, format="PNG", optimize=True)

    return str(styled_path)