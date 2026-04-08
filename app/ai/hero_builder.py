from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from rembg import remove


CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920


def _create_luxury_background(width: int, height: int) -> Image.Image:
    bg = Image.new("RGBA", (width, height), (8, 10, 18, 255))
    px = bg.load()

    top_color = (10, 14, 24)
    mid_color = (16, 18, 30)
    bottom_color = (22, 14, 34)

    for y in range(height):
        t = y / (height - 1)

        if t < 0.55:
            local_t = t / 0.55
            r = int(top_color[0] * (1 - local_t) + mid_color[0] * local_t)
            g = int(top_color[1] * (1 - local_t) + mid_color[1] * local_t)
            b = int(top_color[2] * (1 - local_t) + mid_color[2] * local_t)
        else:
            local_t = (t - 0.55) / 0.45
            r = int(mid_color[0] * (1 - local_t) + bottom_color[0] * local_t)
            g = int(mid_color[1] * (1 - local_t) + bottom_color[1] * local_t)
            b = int(mid_color[2] * (1 - local_t) + bottom_color[2] * local_t)

        for x in range(width):
            px[x, y] = (r, g, b, 255)

    return bg


def _radial_light(width: int, height: int, center, radius, color, blur=80, opacity=180) -> Image.Image:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=opacity)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))

    light = Image.new("RGBA", (width, height), color + (0,))
    light.putalpha(mask)
    return light


def _ellipse_glow(width: int, height: int, bbox, color, blur=70, opacity=170) -> Image.Image:
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(bbox, fill=opacity)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))

    glow = Image.new("RGBA", (width, height), color + (0,))
    glow.putalpha(mask)
    return glow


def _create_floor_shadow(prod_size, blur=35, opacity=90) -> Image.Image:
    w, h = prod_size
    shadow_w = int(w * 0.68)
    shadow_h = int(h * 0.10)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    x1 = (w - shadow_w) // 2
    y1 = int(h * 0.83)
    x2 = x1 + shadow_w
    y2 = y1 + shadow_h

    draw.ellipse((x1, y1, x2, y2), fill=opacity)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))

    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.putalpha(mask)
    return shadow


def _soft_product_shadow(alpha: Image.Image, blur=28, opacity=85, offset=(0, 26)) -> Image.Image:
    w, h = alpha.size
    shadow = Image.new("RGBA", (w + offset[0] + 80, h + offset[1] + 80), (0, 0, 0, 0))

    base = Image.new("RGBA", alpha.size, (0, 0, 0, opacity))
    cut_shadow = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    cut_shadow = Image.composite(base, cut_shadow, alpha)
    cut_shadow = cut_shadow.filter(ImageFilter.GaussianBlur(blur))

    shadow.alpha_composite(cut_shadow, dest=(40 + offset[0], 40 + offset[1]))
    return shadow


def _enhance_product(product_rgba: Image.Image) -> Image.Image:
    rgb = product_rgba.convert("RGB")
    rgb = ImageEnhance.Brightness(rgb).enhance(1.03)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.10)
    rgb = ImageEnhance.Color(rgb).enhance(1.10)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.10)

    out = rgb.convert("RGBA")
    out.putalpha(product_rgba.getchannel("A"))
    return out


def _clean_alpha_edges(product_rgba: Image.Image) -> Image.Image:
    alpha = product_rgba.getchannel("A")
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.2))
    alpha = alpha.point(lambda p: 255 if p > 18 else 0)
    cleaned = product_rgba.copy()
    cleaned.putalpha(alpha)
    return cleaned


def build_hero_scene(image_path: str) -> str:
    source = Path(image_path)
    if not source.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    output_path = source.parent / f"hero_{source.stem}.png"

    original = Image.open(source).convert("RGBA")

    # Produkt freistellen
    cutout = remove(original).convert("RGBA")
    cutout = _clean_alpha_edges(cutout)

    alpha = cutout.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        raise ValueError("Motiv konnte nicht erkannt werden.")

    cutout = cutout.crop(bbox)
    cutout = _enhance_product(cutout)

    # Canvas
    hero = _create_luxury_background(CANVAS_WIDTH, CANVAS_HEIGHT)

    # Lichtstimmung
    top_spot = _radial_light(
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
        center=(CANVAS_WIDTH // 2, int(CANVAS_HEIGHT * 0.33)),
        radius=330,
        color=(255, 236, 215),
        blur=120,
        opacity=165,
    )
    hero = Image.alpha_composite(hero, top_spot)

    stage_glow = _ellipse_glow(
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
        bbox=(
            int(CANVAS_WIDTH * 0.18),
            int(CANVAS_HEIGHT * 0.72),
            int(CANVAS_WIDTH * 0.82),
            int(CANVAS_HEIGHT * 0.92),
        ),
        color=(214, 86, 150),
        blur=110,
        opacity=120,
    )
    hero = Image.alpha_composite(hero, stage_glow)

    cool_back = _radial_light(
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
        center=(int(CANVAS_WIDTH * 0.50), int(CANVAS_HEIGHT * 0.58)),
        radius=420,
        color=(70, 70, 120),
        blur=160,
        opacity=80,
    )
    hero = Image.alpha_composite(hero, cool_back)

    # Produktgröße
    prod_w, prod_h = cutout.size
    target_h = int(CANVAS_HEIGHT * 0.57)
    scale = target_h / prod_h
    new_w = int(prod_w * scale)
    new_h = int(prod_h * scale)
    cutout = cutout.resize((new_w, new_h), Image.LANCZOS)

    # Position
    x = (CANVAS_WIDTH - new_w) // 2
    y = int(CANVAS_HEIGHT * 0.18)

    # Schatten + Boden
    prod_alpha = cutout.getchannel("A")

    floor_shadow = _create_floor_shadow((CANVAS_WIDTH, CANVAS_HEIGHT), blur=48, opacity=95)
    hero = Image.alpha_composite(hero, floor_shadow)

    soft_shadow = _soft_product_shadow(prod_alpha, blur=24, opacity=70, offset=(0, 26))
    shadow_x = x - 40
    shadow_y = y - 40
    hero.alpha_composite(soft_shadow, dest=(shadow_x, shadow_y))

    # Hinter dem Produkt ein sanfter Glow
    local_glow_mask = prod_alpha.filter(ImageFilter.GaussianBlur(26))
    local_glow = Image.new("RGBA", cutout.size, (255, 244, 236, 0))
    local_glow.putalpha(local_glow_mask.point(lambda p: int(p * 0.28)))
    hero.alpha_composite(local_glow, dest=(x, y))

    # Produkt
    hero.alpha_composite(cutout, dest=(x, y))

    # Dezente Top-Highlights
    rim_light = _radial_light(
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
        center=(CANVAS_WIDTH // 2, int(CANVAS_HEIGHT * 0.20)),
        radius=190,
        color=(255, 250, 245),
        blur=110,
        opacity=55,
    )
    hero = Image.alpha_composite(hero, rim_light)

    hero.save(output_path)
    return str(output_path)