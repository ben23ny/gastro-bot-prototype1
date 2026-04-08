from pydantic_settings import BaseSettings, SettingsConfigDict
import json
from datetime import datetime, timezone
from typing import Any

import redis

from app.config import settings


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self) -> None:
        if not settings.REDIS_URL:
            raise RuntimeError("REDIS_URL fehlt. Bitte in Render setzen.")
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def set_job(self, job_id: str, payload: dict[str, Any]) -> None:
        payload["updated_at"] = _utc_now()
        self.client.set(f"job:{job_id}", json.dumps(payload), ex=60 * 60 * 24)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        raw = self.client.get(f"job:{job_id}")
        if not raw:
            return None
        return json.loads(raw)
