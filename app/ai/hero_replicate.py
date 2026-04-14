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


def build_hero_with_replicate(image_path: str, prompt: str | None = None) -> str:
    token = (settings.REPLICATE_API_TOKEN or "").strip()

    if not token:
        raise RuntimeError("REPLICATE_API_TOKEN fehlt oder ist leer in der .env-Datei.")

    source = Path(image_path)
    if not source.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    final_prompt = prompt or settings.REPLICATE_HERO_PROMPT
    client = replicate.Client(api_token=token)

    with open(source, "rb") as image_file:
        output = client.run(
            settings.REPLICATE_HERO_MODEL,
            input={
                "input_image": image_file,
                "prompt": final_prompt,
            },
        )

    output_url = _normalize_replicate_output(output)

    return save_remote_file(
        output_url,
        prefix="hero_",
        suffix=".png",
    )