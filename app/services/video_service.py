from app.ai.video_finalize import add_endcard_to_video
from app.ai.video_replicate import build_video_with_replicate
from app.video_profiles import build_video_prompt


def generate_ai_video(
    hero_image_path: str,
    video_style: str,
    duration_seconds: int,
    logo_path: str,
    headline: str,
    subline: str,
    endcard_seconds: int,
) -> str:
    prompt = build_video_prompt(video_style)
    raw_video_path = build_video_with_replicate(
        image_path=hero_image_path,
        prompt=prompt,
        duration_seconds=duration_seconds,
    )
    return add_endcard_to_video(
        video_path=raw_video_path,
        logo_path=logo_path,
        headline=headline,
        subline=subline,
        endcard_seconds=endcard_seconds,
    )