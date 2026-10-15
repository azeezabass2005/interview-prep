from datetime import datetime
from typing import Optional

from ..config import DEFAULT_MAX_ATTEMPTS
from ..db import Database
from ..errors import NotFound, QueueError
from ..repositories.jobs import JobRepository


def parse_run_at(value: Optional[str], now: datetime) -> datetime:
    """Client timestamps carry an offset; we store naive UTC."""
    if value is None:
        return now
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise QueueError("run_at must be ISO-8601")
    if parsed.tzinfo is None:
        raise QueueError("run_at must include a UTC offset")
    return parsed.replace(tzinfo=None)


class JobQueue:
    def __init__(self, db: Database, clock):
        self._jobs = JobRepository(db)
        self._clock = clock

    def submit(self, kind: str, payload: dict, run_at: Optional[str] = None,
               max_attempts: int = DEFAULT_MAX_ATTEMPTS) -> int:
        if not kind:
            raise QueueError("kind is required")
        if max_attempts < 1:
            raise QueueError("max_attempts must be at least 1")
        return self._jobs.enqueue(kind, payload, parse_run_at(run_at, self._clock.now()), max_attempts)

    def get(self, job_id: int):
        job = self._jobs.get(job_id)
        if job is None:
            raise NotFound(str(job_id))
        return job

    def dead_letters(self):
        return self._jobs.dead()
