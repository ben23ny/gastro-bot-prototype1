from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.core.jobs import create_job_id
from app.core.orchestrator import run_generation_job
from app.models import HealthResponse
from app.services import get_welcome_message
from app.services.job_store import JobStore
from app.services.media_store import save_logo_file, save_upload_file

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
    redis_url = (settings.REDIS_URL or "").strip()

    return {
        "replicate_token_loaded": bool(token),
        "replicate_token_prefix": token[:8] if token else "",
        "redis_loaded": bool(redis_url),
        "hero_model": settings.REPLICATE_HERO_MODEL,
        "video_model": settings.REPLICATE_VIDEO_MODEL,
        "logo_path": settings.VIDEO_LOGO_PATH,
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
            "job_id": None,
            "error": None,
        },
    )


@router.post("/upload", response_class=HTMLResponse)
async def upload_image_page(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    logo: UploadFile | None = File(None),
    headline: str = Form("Sie sind herzlich willkommen"),
    subline: str = Form("Genuss, der Lust auf mehr macht"),
    style_profile: str = Form("luxury"),
    video_mode: str = Form("eco"),
    video_style: str = Form("auto"),
    variant_count: int = Form(3),
):
    try:
        image_path = save_upload_file(file)

        final_logo_path = settings.VIDEO_LOGO_PATH
        if logo and logo.filename:
            final_logo_path = save_logo_file(logo)

        job_id = create_job_id()
        store = JobStore()
        store.set_job(
            job_id,
            {
                "status": "queued",
                "step": "Job wurde angelegt",
                "progress": 0,
                "message": "Die Verarbeitung startet in wenigen Sekunden.",
            },
        )

        background_tasks.add_task(
            run_generation_job,
            job_id,
            image_path,
            final_logo_path,
            headline,
            subline,
            style_profile,
            video_mode,
            video_style,
            variant_count,
        )

        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "app_name": settings.APP_NAME,
                "job_id": job_id,
                "error": None,
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "app_name": settings.APP_NAME,
                "job_id": None,
                "error": str(e),
            },
            status_code=500,
        )


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    store = JobStore()
    job = store.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JSONResponse(job)