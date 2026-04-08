from dataclasses import dataclass


@dataclass
class BrandingConfig:
    headline: str
    subline: str
    style_profile: str
    logo_path: str


STYLE_PROFILES = {
    "luxury": {
        "hero_prompt": (
            "Transform this restaurant snapshot into a premium luxury dessert advertisement. "
            "Keep the exact dessert recognizable. Use elegant studio lighting, dark refined background, "
            "high-end food photography, premium editorial feel, realistic product details, "
            "natural but appetizing colors, no cartoon look, no surreal changes."
        ),
    },
    "social": {
        "hero_prompt": (
            "Transform this product photo into a bold modern Instagram dessert advertisement. "
            "Keep the exact dessert recognizable. Create an eye-catching premium social media look, "
            "clean dramatic background, vibrant appetizing colors, realistic food-commercial quality."
        ),
    },
    "fresh": {
        "hero_prompt": (
            "Transform this dessert photo into a bright fresh premium food advertisement. "
            "Keep the exact product recognizable. Use soft clean light, appetizing freshness, "
            "elegant modern background, realistic food photography."
        ),
    },
    "dark": {
        "hero_prompt": (
            "Transform this dessert photo into a dark dramatic premium advertisement. "
            "Keep the exact product recognizable. Use moody cinematic lighting, strong contrast, "
            "elegant dark background, luxury premium food styling."
        ),
    },
}


def normalize_style_profile(style_profile: str | None) -> str:
    value = (style_profile or "luxury").strip().lower()
    return value if value in STYLE_PROFILES else "luxury"


def build_branding_config(
    headline: str,
    subline: str,
    style_profile: str,
    logo_path: str,
) -> BrandingConfig:
    return BrandingConfig(
        headline=headline.strip(),
        subline=subline.strip(),
        style_profile=normalize_style_profile(style_profile),
        logo_path=logo_path,
    )


def build_hero_prompt(style_profile: str) -> str:
    style = normalize_style_profile(style_profile)
    return STYLE_PROFILES[style]["hero_prompt"]