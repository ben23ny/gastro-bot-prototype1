import traceback

from app.core.jobs import set_progress
from app.core.schemas import GenerationResult, VariantResult
from app.features.branding import build_branding_config
from app.features.captions import build_caption_bundle
from app.features.variants import build_variant_plans
from app.services.hero_service import generate_hero_image
from app.services.job_store import JobStore
from app.services.local_video_service import generate_local_video
from app.services.media_store import get_image_dimensions, to_public_path
from app.services.video_service import generate_ai_video
from app.video_profiles import build_video_mode_config


def run_generation_job(
    job_id: str,
    image_path: str,
    logo_path: str,
    headline: str,
    subline: str,
    style_profile: str,
    video_mode: str,
    video_style: str,
    variant_count: int,
) -> None:
    store = JobStore()

    try:
        branding = build_branding_config(
            headline=headline,
            subline=subline,
            style_profile=style_profile,
            logo_path=logo_path,
        )

        mode_config = build_video_mode_config(video_mode, video_style)
        variant_plans = build_variant_plans(
            base_style_profile=branding.style_profile,
            base_video_style=mode_config.style,
            variant_count=variant_count,
        )

        original_width, original_height = get_image_dimensions(image_path)
        variants_result: list[VariantResult] = []

        total = len(variant_plans)

        for idx, plan in enumerate(variant_plans, start=1):
            base_progress = 10 + int(((idx - 1) / total) * 75)

            set_progress(
                store,
                job_id,
                "processing",
                f"{plan.label}: Hero-Bild wird erzeugt",
                base_progress,
                f"{plan.label} läuft mit Stil '{plan.style_profile}' und Effekt '{plan.video_style}'.",
            )

            hero_path = generate_hero_image(image_path, plan.style_profile)
            hero_width, hero_height = get_image_dimensions(hero_path)

            set_progress(
                store,
                job_id,
                "processing",
                f"{plan.label}: Video wird erzeugt",
                min(base_progress + 15, 90),
                f"{plan.label} wird im Modus '{mode_config.mode}' erzeugt.",
            )

            if mode_config.use_ai_video:
                final_video_path = generate_ai_video(
                    hero_image_path=hero_path,
                    video_style=plan.video_style,
                    duration_seconds=mode_config.ai_duration_seconds,
                    logo_path=branding.logo_path,
                    headline=branding.headline,
                    subline=branding.subline,
                    endcard_seconds=mode_config.final_endcard_seconds,
                )
            else:
                final_video_path = generate_local_video(
                    hero_image_path=hero_path,
                    video_style=plan.video_style,
                    logo_path=branding.logo_path,
                    headline=branding.headline,
                    subline=branding.subline,
                    endcard_seconds=mode_config.final_endcard_seconds,
                )

            caption = build_caption_bundle(
                headline=branding.headline,
                subline=branding.subline,
                style_profile=plan.style_profile,
            )

            variants_result.append(
                VariantResult(
                    label=plan.label,
                    style_profile=plan.style_profile,
                    video_mode=mode_config.mode,
                    video_style=plan.video_style,
                    hero_image=to_public_path(hero_path),
                    video=to_public_path(final_video_path),
                    hero_width=hero_width,
                    hero_height=hero_height,
                    caption=caption,
                )
            )

        result = GenerationResult(
            original_image=to_public_path(image_path),
            original_width=original_width,
            original_height=original_height,
            headline=branding.headline,
            subline=branding.subline,
            variant_count=len(variants_result),
            variants=variants_result,
        )

        store.set_job(
            job_id,
            {
                "status": "done",
                "step": "Abgeschlossen",
                "progress": 100,
                "message": "Dein Variantenpaket wurde erfolgreich erstellt.",
                "result": result.to_dict(),
            },
        )

    except Exception as e:
        store.set_job(
            job_id,
            {
                "status": "failed",
                "step": "Fehlgeschlagen",
                "progress": 100,
                "message": "Die Verarbeitung konnte nicht abgeschlossen werden.",
                "error": str(e),
                "traceback": traceback.format_exc(),
            },
        )