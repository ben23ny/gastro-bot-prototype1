from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove


def create_focus_image(image_path: str) -> str:
    source = Path(image_path)

    if not source.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    output_path = source.parent / f"focus_{source.stem}.png"

    # Bild laden
    input_image = Image.open(source).convert("RGBA")

    # KI-basierte Freistellung
    foreground = remove(input_image)

    # Hintergrund erstellen (unscharf + dunkler)
    background = Image.open(source).convert("RGB")
    background = background.filter(ImageFilter.GaussianBlur(18))

    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.75)

    background = background.convert("RGBA")

    # Vordergrund leicht optimieren
    fg_rgb = foreground.convert("RGB")

    fg_rgb = ImageEnhance.Brightness(fg_rgb).enhance(1.06)
    fg_rgb = ImageEnhance.Contrast(fg_rgb).enhance(1.12)
    fg_rgb = ImageEnhance.Color(fg_rgb).enhance(1.15)
    fg_rgb = ImageEnhance.Sharpness(fg_rgb).enhance(1.25)

    fg_rgba = fg_rgb.convert("RGBA")

    # Kombinieren
    final = Image.alpha_composite(background, fg_rgba)

    final.save(output_path)

    return str(output_path)