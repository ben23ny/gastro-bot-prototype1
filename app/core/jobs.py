import uuid

from app.core.schemas import ProgressState
from app.services.job_store import JobStore


def create_job_id() -> str:
    return uuid.uuid4().hex


def set_progress(
    store: JobStore,
    job_id: str,
    status: str,
    step: str,
    progress: int,
    message: str | None = None,
) -> None:
    state = ProgressState(
        status=status,
        step=step,
        progress=progress,
        message=message,
    )
    store.set_job(job_id, state.to_dict())