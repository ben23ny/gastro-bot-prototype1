import random
from dataclasses import dataclass


@dataclass
class VideoModeConfig:
    mode: str
    style: str
    use_ai_video: bool
    ai_duration_seconds: int
    final_endcard_seconds: int


VALID_MODES = {"eco", "pro", "premium"}
VALID_STYLES = {
    "auto",
    "cinematic_push",
    "soft_float",
    "dramatic_focus",
    "luxury_glow",
}


VIDEO_PROMPTS = {
    "cinematic_push": (
        "Create a premium dessert advertisement video from this hero image. "
        "Use a slow cinematic push-in camera move, subtle realism, elegant product focus, "
        "no morphing, no deformation, realistic premium food commercial feel."
    ),
    "soft_float": (
        "Create a premium dessert ad video from this hero image with gentle floating camera motion, "
        "soft elegant movement, natural premium realism, no object deformation, no surreal motion."
    ),
    "dramatic_focus": (
        "Create a dramatic premium dessert ad video from this hero image with moody focus transitions, "
        "subtle cinematic movement, elegant premium lighting, realistic motion only, no morphing."
    ),
    "luxury_glow": (
        "Create a luxury dessert commercial video from this hero image with subtle glow highlights, "
        "gentle premium camera movement, refined commercial realism, no floating objects, no distortion."
    ),
}


def normalize_mode(value: str | None) -> str:
    mode = (value or "eco").strip().lower()
    return mode if mode in VALID_MODES else "eco"


def normalize_style(value: str | None) -> str:
    style = (value or "auto").strip().lower()
    return style if style in VALID_STYLES else "auto"


def resolve_style(style: str) -> str:
    normalized = normalize_style(style)
    if normalized != "auto":
        return normalized

    return random.choice(
        ["cinematic_push", "soft_float", "dramatic_focus", "luxury_glow"]
    )


def build_video_mode_config(mode: str | None, style: str | None) -> VideoModeConfig:
    final_mode = normalize_mode(mode)
    final_style = resolve_style(style)

    if final_mode == "eco":
        return VideoModeConfig(
            mode="eco",
            style=final_style,
            use_ai_video=False,
            ai_duration_seconds=0,
            final_endcard_seconds=2,
        )

    if final_mode == "pro":
        return VideoModeConfig(
            mode="pro",
            style=final_style,
            use_ai_video=True,
            ai_duration_seconds=3,
            final_endcard_seconds=2,
        )

    return VideoModeConfig(
        mode="premium",
        style=final_style,
        use_ai_video=True,
        ai_duration_seconds=5,
        final_endcard_seconds=2,
    )


def build_video_prompt(style: str) -> str:
    normalized = normalize_style(style)
    if normalized == "auto":
        normalized = resolve_style("auto")
    return VIDEO_PROMPTS.get(normalized, VIDEO_PROMPTS["cinematic_push"])
