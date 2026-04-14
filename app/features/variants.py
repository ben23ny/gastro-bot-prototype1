from dataclasses import dataclass

from app.features.branding import normalize_style_profile


@dataclass
class VariantPlan:
    label: str
    style_profile: str
    video_style: str


STYLE_ROTATIONS = {
    "luxury": ["luxury", "social", "dark"],
    "social": ["social", "fresh", "luxury"],
    "fresh": ["fresh", "social", "luxury"],
    "dark": ["dark", "luxury", "social"],
}

VIDEO_ROTATIONS = {
    "auto": ["cinematic_push", "soft_float", "dramatic_focus"],
    "cinematic_push": ["cinematic_push", "luxury_glow", "soft_float"],
    "soft_float": ["soft_float", "cinematic_push", "luxury_glow"],
    "dramatic_focus": ["dramatic_focus", "cinematic_push", "luxury_glow"],
    "luxury_glow": ["luxury_glow", "cinematic_push", "soft_float"],
}


def normalize_variant_count(value: int | str | None) -> int:
    try:
        count = int(value or 1)
    except (TypeError, ValueError):
        count = 1
    return max(1, min(3, count))


def build_variant_plans(
    base_style_profile: str,
    base_video_style: str,
    variant_count: int,
) -> list[VariantPlan]:
    count = normalize_variant_count(variant_count)
    style_profile = normalize_style_profile(base_style_profile)
    video_style = (base_video_style or "auto").strip().lower()

    style_rotation = STYLE_ROTATIONS.get(style_profile, STYLE_ROTATIONS["luxury"])
    video_rotation = VIDEO_ROTATIONS.get(video_style, VIDEO_ROTATIONS["auto"])

    plans: list[VariantPlan] = []
    for idx in range(count):
        plans.append(
            VariantPlan(
                label=f"Variante {idx + 1}",
                style_profile=style_rotation[idx],
                video_style=video_rotation[idx],
            )
        )
    return plans