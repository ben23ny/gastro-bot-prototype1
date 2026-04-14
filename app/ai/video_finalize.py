import shutil
import subprocess
import uuid
from pathlib import Path

from app.storage.file_manager import VIDEO_DIR, ensure_video_dir


def _check_ffmpeg() -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg wurde nicht gefunden.")


def _escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", r"\'")
        .replace(",", r"\,")
        .replace("%", r"\%")
    )


def add_endcard_to_video(
    video_path: str,
    logo_path: str,
    headline: str,
    subline: str,
    endcard_seconds: int = 2,
) -> str:
    _check_ffmpeg()
    ensure_video_dir()

    source = Path(video_path)
    if not source.exists():
        raise FileNotFoundError(f"Video nicht gefunden: {video_path}")

    logo = Path(logo_path)
    if not logo.exists():
        raise FileNotFoundError(f"Logo nicht gefunden: {logo_path}")

    output_path = VIDEO_DIR / f"final_{uuid.uuid4().hex}.mp4"

    headline_escaped = _escape_drawtext(headline)
    subline_escaped = _escape_drawtext(subline)

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,"
        "setsar=1,format=yuv420p[main];"
        "[1:v]scale=340:-1[logo];"
        f"color=c=0x090b14:s=1080x1920:d={endcard_seconds}[endbg];"
        "[endbg][logo]overlay=(W-w)/2:430[tmp1];"
        f"[tmp1]drawtext=text='{headline_escaped}':"
        "fontcolor=white:fontsize=64:x=(w-text_w)/2:y=980:"
        "shadowcolor=black@0.55:shadowx=2:shadowy=2[tmp2];"
        f"[tmp2]drawtext=text='{subline_escaped}':"
        "fontcolor=white@0.82:fontsize=32:x=(w-text_w)/2:y=1080:"
        "shadowcolor=black@0.45:shadowx=2:shadowy=2[endcard];"
        "[main][endcard]concat=n=2:v=1:a=0[vout]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(source),
        "-loop", "1",
        "-t", str(endcard_seconds),
        "-i", str(logo),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-r", "30",
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
            "Fehler bei der Endcard-Erzeugung:\n"
            f"{result.stderr}"
        )

    return str(output_path)