import json
from dataclasses import dataclass
from datetime import timedelta

from .clock import iso

JOBS_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL,
    run_at TEXT NOT NULL,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_jobs_due ON jobs (status, run_at);
"""


@dataclass
class Job:
    id: str
    kind: str
    payload: dict
    status: str
    attempts: int
    max_attempts: int
    run_at: str
    last_error: str | None


def _job(row) -> Job:
    return Job(row["id"], row["kind"], json.loads(row["payload"]), row["status"], row["attempts"], row["max_attempts"],
               row["run_at"], row["last_error"])


class JobQueue:
    """A durable job queue in the service database, shared by every worker process."""

    def __init__(self, db, clock, ids):
        self._db = db
        self._clock = clock
        self._ids = ids

    def enqueue(self, kind: str, payload: dict, delay_seconds: int = 0, max_attempts: int = 5) -> str:
        now = self._clock.now()
        job_id = self._ids.new("job")
        self._db.execute(
            "INSERT INTO jobs (id, kind, payload, status, attempts, max_attempts, run_at, created_at, updated_at) "
            "VALUES (?, ?, ?, 'queued', 0, ?, ?, ?, ?)",
            (job_id, kind, json.dumps(payload), max_attempts, iso(now + timedelta(seconds=delay_seconds)), iso(now), iso(now)),
        )
        return job_id

    def due(self, limit: int = 100) -> list[Job]:
        rows = self._db.query(
            "SELECT * FROM jobs WHERE status = 'queued' AND run_at <= ? ORDER BY run_at, id LIMIT ?",
            (iso(self._clock.now()), limit),
        )
        return [_job(r) for r in rows]

    def claim(self, job_id: str) -> bool:
        changed = self._db.execute(
            "UPDATE jobs SET status = 'running', attempts = attempts + 1, updated_at = ? WHERE id = ?",
            (iso(self._clock.now()), job_id),
        )
        return changed == 1

    def complete(self, job_id: str) -> None:
        self._db.execute("UPDATE jobs SET status = 'done', updated_at = ? WHERE id = ?", (iso(self._clock.now()), job_id))

    def fail(self, job_id: str, error: str, retry_in_seconds: int) -> str:
        job = self.get(job_id)
        now = self._clock.now()
        status = "dead" if job.attempts >= job.max_attempts else "queued"
        self._db.execute(
            "UPDATE jobs SET status = ?, last_error = ?, run_at = ?, updated_at = ? WHERE id = ?",
            (status, error[:500], iso(now + timedelta(seconds=retry_in_seconds)), iso(now), job_id),
        )
        return status

    def get(self, job_id: str) -> Job:
        return _job(self._db.query_one("SELECT * FROM jobs WHERE id = ?", (job_id,)))

    def by_status(self, status: str) -> list[Job]:
        return [_job(r) for r in self._db.query("SELECT * FROM jobs WHERE status = ? ORDER BY created_at, id", (status,))]


def backoff_seconds(attempt: int, base: int = 30, cap: int = 3600) -> int:
    return max(cap, base * 2 ** (attempt - 1))


class Worker:
    """Runs due jobs. Several worker processes may run against the same queue."""

    def __init__(self, queue: JobQueue, handlers: dict, logger):
        self._queue = queue
        self._handlers = handlers
        self._logger = logger

    def run_pending(self, limit: int = 100) -> int:
        processed = 0
        for job in self._queue.due(limit):
            if not self._queue.claim(job.id):
                continue
            processed += 1
            try:
                self._handlers[job.kind](job.payload)
            except Exception as e:
                attempt = job.attempts + 1
                status = self._queue.fail(job.id, f"{type(e).__name__}: {e}", backoff_seconds(attempt))
                self._logger.warning("job_failed", job_id=job.id, kind=job.kind, attempt=attempt, status=status, error=str(e))
            else:
                self._queue.complete(job.id)
        return processed
