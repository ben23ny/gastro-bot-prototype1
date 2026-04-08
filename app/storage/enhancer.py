from pathlib import Path
from typing import Any

import replicate

from app.config import settings
from app.storage.file_manager import save_remote_file


def _normalize_replicate_output(output: Any) -> str:
    if output is None:
        raise RuntimeError("Replicate hat kein Ergebnis zurückgegeben.")

    if isinstance(output, list):
        if not output:
            raise RuntimeError("Replicate-Ausgabe ist leer.")
        output = output[0]

    if isinstance(output, str):
        return output

    if hasattr(output, "url"):
        url_value = output.url
        if callable(url_value):
            return url_value()
        return str(url_value)

    return str(output)


def enhance_image(image_path: str) -> str:
    if not settings.REPLICATE_API_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN fehlt in der .env-Datei.")

    source = Path(image_path)
    if not source.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    with open(source, "rb") as image_file:
        output = replicate.run(
            settings.REPLICATE_ENHANCER_MODEL,
            input={
                "image": image_file,
                "scale": settings.REPLICATE_ENHANCER_SCALE,
                "model": settings.REPLICATE_ENHANCER_MODE,
                "face_enhancement": settings.REPLICATE_FACE_ENHANCE,
            },
        )

    output_url = _normalize_replicate_output(output)

    enhanced_local_path = save_remote_file(
        output_url,
        prefix="enhanced_",
        suffix=".png",
    )

    return enhanced_local_path