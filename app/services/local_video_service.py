from app.ai.video_finalize import add_endcard_to_video
from app.ai.video_local import create_local_video_from_hero


def generate_local_video(
    hero_image_path: str,
    video_style: str,
    logo_path: str,
    headline: str,
    subline: str,
    endcard_seconds: int,
) -> str:
    raw_video_path = create_local_video_from_hero(
        image_path=hero_image_path,
        style=video_style,
        duration=4,
    )
    return add_endcard_to_video(
        video_path=raw_video_path,
        logo_path=logo_path,
        headline=headline,
        subline=subline,
        endcard_seconds=endcard_seconds,
    )