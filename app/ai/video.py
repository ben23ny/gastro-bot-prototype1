import shutil
import subprocess
import uuid
from pathlib import Path

from app.storage.file_manager import ensure_video_dir, VIDEO_DIR


def _check_ffmpeg() -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg wurde nicht gefunden. Bitte ffmpeg korrekt installieren.")


def create_cinematic_video(
    image_path: str,
    duration: int = 6,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920,
) -> str:
    """
    Erstellt aus einem einzelnen Bild ein hochwertiges MP4 im Hochformat.
    Stil:
    - langsamer Zoom-In
    - leichte vertikale Bewegung
    - saubere H.264-Ausgabe
    """

    _check_ffmpeg()
    ensure_video_dir()

    source = Path(image_path)
    if not source.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    output_filename = f"cinematic_{uuid.uuid4().hex}.mp4"
    output_path = VIDEO_DIR / output_filename

    total_frames = duration * fps

    # Der Filter macht:
    # 1. Bild auf Hochformat-Bühne einpassen
    # 2. leicht vergrößern, damit Zoom-Reserven vorhanden sind
    # 3. sanften Zoom-In über die Zeit
    # 4. leichte vertikale Drift
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan="
        f"z='min(1.0+0.0009*on,1.08)':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)-on*0.15':"
        f"d={total_frames}:"
        f"s={width}x{height}:"
        f"fps={fps},"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", str(source),
        "-t", str(duration),
        "-vf", vf,
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            "Fehler bei der Video-Erzeugung mit ffmpeg:\n"
            f"{result.stderr}"
        )

    return str(output_path)