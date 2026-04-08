from pathlib import Path
from typing import Any

import replicate

from app.config import settings
from app.storage.file_manager import save_remote_video


def _normalize_replicate_output(output: Any) -> str:
    if output is None:
        raise RuntimeError("Replicate hat kein Video-Ergebnis zurückgegeben.")

    if isinstance(output, list):
        if not output:
            raise RuntimeError("Replicate-Videoausgabe ist leer.")
        output = output[0]

    if isinstance(output, str):
        return output

    if hasattr(output, "url"):
        url_value = output.url
        if callable(url_value):
            return url_value()
        return str(url_value)

    return str(output)


def build_video_with_replicate(
    image_path: str,
    prompt: str,
    duration_seconds: int,
) -> str:
    token = (settings.REPLICATE_API_TOKEN or "").strip()

    if not token:
        raise RuntimeError("REPLICATE_API_TOKEN fehlt oder ist leer in der .env-Datei.")

    source = Path(image_path)
    if not source.exists():
        raise FileNotFoundError(f"Hero-Bild nicht gefunden: {image_path}")

    client = replicate.Client(api_token=token)

    with open(source, "rb") as image_file:
        output = client.run(
            settings.REPLICATE_VIDEO_MODEL,
            input={
                "image": image_file,
                "prompt": prompt,
                "duration": duration_seconds,
            },
        )

    output_url = _normalize_replicate_output(output)

    return save_remote_video(
        output_url,
        prefix="wan_",
        suffix=".mp4",
    )