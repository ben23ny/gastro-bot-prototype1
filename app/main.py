from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router
from app.utils import setup_logging

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)