from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
import fastapi.templating

import app.ai.food_styler
from app.ai.hero_replicate import build_hero_with_replicate
from app.ai.video_replicate import build_video_with_replicate
from app.ai.video_local import create_local_video_from_hero
from app.ai.video_finalize import add_endcard_to_video
from app.branding import (
    build_branding_config,
    build_hero_prompt,
)

from app.captions import build_caption_bundle
from app.config import settings
from app.models import HealthResponse, UploadResponse, VideoResponse
from app.services import get_welcome_message
from app.storage.file_manager import (
    save_upload_file,
    save_logo_file,
    to_public_path,
    get_image_dimensions,
)
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


STYLE_VIDEO_PROMPTS = {
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


def build_video_prompt_for_style(style: str) -> str:
    return STYLE_VIDEO_PROMPTS.get(style, STYLE_VIDEO_PROMPTS["cinematic_push"])

router = APIRouter()
templates = fastapi.templating.Jinja2Templates(directory="templates")


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )


@router.get("/debug/config")
def debug_config():
    token = (settings.REPLICATE_API_TOKEN or "").strip()
    return {
        "replicate_token_loaded": bool(token),
        "replicate_token_length": len(token),
        "replicate_token_prefix": token[:8] if token else "",
        "hero_model": settings.REPLICATE_HERO_MODEL,
        "video_model": settings.REPLICATE_VIDEO_MODEL,
        "default_logo_path": settings.VIDEO_LOGO_PATH,
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "welcome_message": get_welcome_message(),
        },
    )


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "app_name": settings.APP_NAME,
            "result": None,
            "video_result": None,
            "caption_result": None,
            "error": None,
        },
    )


@router.post("/upload", response_class=HTMLResponse)
async def upload_image_page(
    request: Request,
    file: UploadFile = File(...),
    logo: UploadFile | None = File(None),
    headline: str = Form("Sie sind herzlich willkommen"),
    subline: str = Form("Genuss, der Lust auf mehr macht"),
    style_profile: str = Form("luxury"),
    video_mode: str = Form("eco"),
    video_style: str = Form("auto"),
):
    try:
        saved_path = save_upload_file(file)
        styled_path = app.ai.food_styler.apply_food_style(saved_path)

        final_logo_path = settings.VIDEO_LOGO_PATH
        if logo and logo.filename:
            final_logo_path = save_logo_file(logo)

        branding = build_branding_config(
            headline=headline,
            subline=subline,
            style_profile=style_profile,
            logo_path=final_logo_path,
        )

        hero_prompt = build_hero_prompt(branding.style_profile)
        hero_path = build_hero_with_replicate(styled_path, hero_prompt)

        mode_config = build_video_mode_config(video_mode, video_style)
        video_prompt = build_video_prompt_for_style(mode_config.style)

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

        original_width, original_height = get_image_dimensions(saved_path)
        final_width, final_height = get_image_dimensions(hero_path)

        result = {
            "status": "success",
            "original_image": to_public_path(saved_path),
            "enhanced_image": to_public_path(hero_path),
            "original_width": original_width,
            "original_height": original_height,
            "enhanced_width": final_width,
            "enhanced_height": final_height,
            "detail": f"Bild wurde im Stil '{branding.style_profile}' in ein Hero-Werbemotiv umgewandelt.",
        }

        video_result = {
            "status": "success",
            "image": to_public_path(hero_path),
            "video": to_public_path(final_video_path),
            "detail": (
                f"Video wurde im Modus '{mode_config.mode}' "
                f"mit dem Effekt '{mode_config.style}' erzeugt."
            ),
        }

        caption_result = {
            "instagram_caption": caption_bundle.instagram_caption,
            "hashtags": caption_bundle.hashtags,
            "story_text": caption_bundle.story_text,
            "promo_text": caption_bundle.promo_text,
        }

        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "app_name": settings.APP_NAME,
                "result": result,
                "video_result": video_result,
                "caption_result": caption_result,
                "error": None,
            },
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "app_name": settings.APP_NAME,
                "result": None,
                "video_result": None,
                "caption_result": None,
                "error": str(e),
            },
            status_code=400,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "app_name": settings.APP_NAME,
                "result": None,
                "video_result": None,
                "caption_result": None,
                "error": f"Fehler bei der Bild-/Video-Erzeugung: {e}",
            },
            status_code=500,
        )


@router.post("/api/upload", response_model=UploadResponse)
async def upload_image_api(file: UploadFile = File(...)):
    try:
        saved_path = save_upload_file(file)
        styled_path = app.ai.food_styler.apply_food_style(saved_path)
        hero_prompt = build_hero_prompt("luxury")
        hero_path = build_hero_with_replicate(styled_path, hero_prompt)

        original_width, original_height = get_image_dimensions(saved_path)
        final_width, final_height = get_image_dimensions(hero_path)

        return UploadResponse(
            status="success",
            original_image=to_public_path(saved_path),
            enhanced_image=to_public_path(hero_path),
            original_width=original_width,
            original_height=original_height,
            enhanced_width=final_width,
            enhanced_height=final_height,
            detail="Bild wurde in ein Luxury-Hero-Werbemotiv umgewandelt.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hero-Fehler: {e}")


@router.post("/api/video", response_model=VideoResponse)
async def create_video_api(file: UploadFile = File(...)):
    try:
        saved_path = save_upload_file(file)
        styled_path = app.ai.food_styler.apply_food_style(saved_path)
        hero_prompt = build_hero_prompt("luxury")
        hero_path = build_hero_with_replicate(styled_path, hero_prompt)

        mode_config = build_video_mode_config("eco", "auto")
        raw_video_path = create_local_video_from_hero(
            image_path=hero_path,
            style=mode_config.style,
            duration=4,
        )

        final_video_path = add_endcard_to_video(
            video_path=raw_video_path,
            logo_path=settings.VIDEO_LOGO_PATH,
            headline=settings.VIDEO_ENDCARD_HEADLINE,
            subline=settings.VIDEO_ENDCARD_SUBLINE,
            endcard_seconds=mode_config.final_endcard_seconds,
        )

        return VideoResponse(
            status="success",
            image=to_public_path(hero_path),
            video=to_public_path(final_video_path),
            detail="Video wurde erzeugt.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video-Fehler: {e}")