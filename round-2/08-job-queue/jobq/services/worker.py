from datetime import timedelta
from typing import Optional

from ..config import LEASE_SECONDS
from ..db import Database
from ..errors import LeaseLost
from ..handlers_registry import HandlerRegistry
from ..models import Job
from ..repositories.jobs import JobRepository
from .backoff import retry_delay_seconds


class JobContext:
    def __init__(self, worker: "Worker", job: Job):
        self._worker = worker
        self.job = job

    def heartbeat(self) -> None:
        self._worker.heartbeat(self.job)


class Worker:
    def __init__(self, db: Database, clock, registry: HandlerRegistry, worker_id: str):
        self._jobs = JobRepository(db)
        self._clock = clock
        self._registry = registry
        self.worker_id = worker_id

    def heartbeat(self, job: Job) -> None:
        lease_until = job.claimed_at + timedelta(seconds=LEASE_SECONDS)
        if not self._jobs.extend_lease(job.job_id, self.worker_id, lease_until):
            raise LeaseLost(f"job {job.job_id} lease lost")

    def poll_once(self) -> Optional[int]:
        now = self._clock.now()
        candidate = self._jobs.next_candidate(now)
        if candidate is None:
            return None
        if not self._jobs.claim(candidate, self.worker_id, now, now + timedelta(seconds=LEASE_SECONDS)):
            return None
        job = self._jobs.get(candidate.job_id)
        try:
            self._registry.get(job.kind)(job.payload, JobContext(self, job))
        except Exception as exc:
            self._on_failure(job, exc)
            return job.job_id
        self._jobs.complete(job.job_id, self.worker_id)
        return job.job_id

    def _on_failure(self, job: Job, exc: Exception) -> None:
        attempts = job.attempts
        if attempts > job.max_attempts:
            self._jobs.bury(job.job_id, repr(exc))
            return
        delay = retry_delay_seconds(attempts)
        self._jobs.reschedule(job.job_id, self._clock.now() + timedelta(seconds=delay), repr(exc))
