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
