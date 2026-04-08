import traceback
import uuid

from app.ai.food_styler import apply_food_style
from app.ai.hero_replicate import build_hero_with_replicate
from app.ai.video_finalize import add_endcard_to_video
from app.ai.video_local import create_local_video_from_hero
from app.ai.video_replicate import build_video_with_replicate
from app.branding import (
    build_branding_config,
    build_hero_prompt,
)
from app.captions import build_caption_bundle
from app.config import settings
from app.job_store import JobStore
from app.storage.file_manager import (
    get_image_dimensions,
    save_upload_file,
    save_logo_file,
    to_public_path,
)
from app.video_profiles import (
    build_video_mode_config,
    build_video_prompt_for_style,
)


def create_job_id() -> str:
    return uuid.uuid4().hex


def process_generation_job(
    job_id: str,
    image_path: str,
    logo_path: str,
    headline: str,
    subline: str,
    style_profile: str,
    video_mode: str,
    video_style: str,
) -> None:
    store = JobStore()

    try:
        store.set_job(
            job_id,
            {
                "status": "processing",
                "step": "Styling image",
            },
        )

        styled_path = apply_food_style(image_path)

        branding = build_branding_config(
            headline=headline,
            subline=subline,
            style_profile=style_profile,
            logo_path=logo_path,
        )

        store.set_job(
            job_id,
            {
                "status": "processing",
                "step": "Generating hero image",
            },
        )

        hero_prompt = build_hero_prompt(branding.style_profile)
        hero_path = build_hero_with_replicate(styled_path, hero_prompt)

        mode_config = build_video_mode_config(video_mode, video_style)
        video_prompt = build_video_prompt_for_style(mode_config.style)

        store.set_job(
            job_id,
            {
                "status": "processing",
                "step": f"Generating video ({mode_config.mode}, {mode_config.style})",
            },
        )

        if mode_config.use_ai_video:
            raw_video_path = build_video_with_replicate(
                image_path=hero_path,
                prompt=video_prompt,
                duration_seconds=mode_config.ai_duration_seconds,
            )
        else:
            raw_video_path = create_local_video_from_hero(
                image_path=hero_path,
                style=mode_config.style,
                duration=4,
            )

        store.set_job(
            job_id,
            {
                "status": "processing",
                "step": "Finalizing endcard",
            },
        )

        final_video_path = add_endcard_to_video(
            video_path=raw_video_path,
            logo_path=branding.logo_path,
            headline=branding.headline,
            subline=branding.subline,
            endcard_seconds=mode_config.final_endcard_seconds,
        )

        caption_bundle = build_caption_bundle(
            headline=branding.headline,
            subline=branding.subline,
            style_profile=branding.style_profile,
        )

        original_width, original_height = get_image_dimensions(image_path)
        hero_width, hero_height = get_image_dimensions(hero_path)

        store.set_job(
            job_id,
            {
                "status": "done",
                "step": "Completed",
                "result": {
                    "original_image": to_public_path(image_path),
                    "hero_image": to_public_path(hero_path),
                    "video": to_public_path(final_video_path),
                    "original_width": original_width,
                    "original_height": original_height,
                    "hero_width": hero_width,
                    "hero_height": hero_height,
                    "style_profile": branding.style_profile,
                    "video_mode": mode_config.mode,
                    "video_style": mode_config.style,
                    "headline": branding.headline,
                    "subline": branding.subline,
                    "caption": {
                        "instagram_caption": caption_bundle.instagram_caption,
                        "hashtags": caption_bundle.hashtags,
                        "story_text": caption_bundle.story_text,
                        "promo_text": caption_bundle.promo_text,
                    },
                },
            },
        )

    except Exception as e:
        store.set_job(
            job_id,
            {
                "status": "failed",
                "step": "Failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
            },
        )
