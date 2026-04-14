from dataclasses import dataclass


@dataclass
class BrandingConfig:
    headline: str
    subline: str
    style_profile: str
    logo_path: str


def normalize_style_profile(style_profile: str | None) -> str:
    value = (style_profile or "luxury").strip().lower()
    allowed = {"luxury", "social", "fresh", "dark"}
    return value if value in allowed else "luxury"


def build_branding_config(
    headline: str | None,
    subline: str | None,
    style_profile: str | None,
    logo_path: str,
) -> BrandingConfig:
    return BrandingConfig(
        headline=(headline or "Sie sind herzlich willkommen").strip(),
        subline=(subline or "Genuss, der Lust auf mehr macht").strip(),
        style_profile=normalize_style_profile(style_profile),
        logo_path=logo_path,
    )