import uuid
from pathlib import Path
from urllib.request import urlopen

from fastapi import UploadFile
from PIL import Image

UPLOAD_DIR = Path("static/uploads")
VIDEO_DIR = Path("static/videos")
BRANDING_DIR = Path("static/branding")


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def ensure_video_dir() -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def ensure_branding_dir() -> None:
    BRANDING_DIR.mkdir(parents=True, exist_ok=True)


def is_allowed_image(filename: str) -> bool:
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    ext = Path(filename).suffix.lower()
    return ext in allowed


def save_upload_file(upload_file: UploadFile) -> str:
    ensure_upload_dir()

    if not upload_file.filename:
        raise ValueError("Dateiname fehlt.")

    if not is_allowed_image(upload_file.filename):
        raise ValueError("Nur JPG, JPEG, PNG und WEBP sind erlaubt.")

    ext = Path(upload_file.filename).suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return str(file_path)


def save_logo_file(upload_file: UploadFile) -> str:
    ensure_branding_dir()

    if not upload_file.filename:
        raise ValueError("Logo-Dateiname fehlt.")

    ext = Path(upload_file.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("Logo muss PNG, JPG, JPEG oder WEBP sein.")

    filename = f"logo_{uuid.uuid4().hex}{ext}"
    file_path = BRANDING_DIR / filename

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return str(file_path)


def save_remote_file(url: str, prefix: str = "output_", suffix: str = ".png") -> str:
    ensure_upload_dir()

    filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
    output_path = UPLOAD_DIR / filename

    with urlopen(url) as response:
        data = response.read()

    with open(output_path, "wb") as f:
        f.write(data)

    return str(output_path)


def save_remote_video(url: str, prefix: str = "video_", suffix: str = ".mp4") -> str:
    ensure_video_dir()

    filename = f"{prefix}{uuid.uuid4().hex}{suffix}"
    output_path = VIDEO_DIR / filename

    with urlopen(url) as response:
        data = response.read()

    with open(output_path, "wb") as f:
        f.write(data)

    return str(output_path)


def to_public_path(file_path: str) -> str:
    return "/" + file_path.replace("\\", "/")


def get_image_dimensions(file_path: str) -> tuple[int, int]:
    with Image.open(file_path) as img:
        return img.size