import shutil
import subprocess
import uuid
from pathlib import Path

from app.storage.file_manager import VIDEO_DIR, ensure_video_dir


def _check_ffmpeg() -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg wurde nicht gefunden.")


def _run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg Fehler:\n{result.stderr}")


def create_local_video_from_hero(
    image_path: str,
    style: str,
    duration: int = 4,
    fps: int = 30,
    width: int = 1080,
    height: int = 1920,
) -> str:
    _check_ffmpeg()
    ensure_video_dir()

    source = Path(image_path)
    if not source.exists():
        raise FileNotFoundError(f"Hero-Bild nicht gefunden: {image_path}")

    output_path = VIDEO_DIR / f"local_{style}_{uuid.uuid4().hex}.mp4"
    total_frames = duration * fps

    if style == "cinematic_push":
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"zoompan="
            f"z='min(1.0+0.0010*on,1.09)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    elif style == "soft_float":
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"zoompan="
            f"z='min(1.02+0.0005*on,1.06)':"
            f"x='iw/2-(iw/zoom/2)+sin(on/18)*8':"
            f"y='ih/2-(ih/zoom/2)+cos(on/22)*10':"
            f"d={total_frames}:s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    elif style == "dramatic_focus":
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"eq=contrast=1.05:brightness=0.02:saturation=1.08,"
            f"zoompan="
            f"z='min(1.01+0.0012*on,1.10)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)-on*0.10':"
            f"d={total_frames}:s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    else:  # luxury_glow
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"eq=contrast=1.04:brightness=0.015:saturation=1.06,"
            f"zoompan="
            f"z='min(1.015+0.0008*on,1.07)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={total_frames}:s={width}x{height}:fps={fps},"
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

    _run_ffmpeg(cmd)
    return str(output_path)