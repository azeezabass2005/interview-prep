import itertools
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

LEASE = timedelta(seconds=30)
BASE_BACKOFF = timedelta(seconds=10)


class QueueError(Exception):
    pass


@dataclass
class Job:
    job_id: int
    name: str
    priority: int
    run_at: datetime
    max_attempts: int
    unique_key: Optional[str]
    seq: int
    status: str = "PENDING"
    attempts: int = 0
    worker: Optional[str] = None
    lease_until: Optional[datetime] = None


class JobQueue:
    def __init__(self):
        self.jobs = {}
        self._ids = itertools.count(1)

    def enqueue(self, name, now, priority=3, run_at=None, max_attempts=3, unique_key=None):
        if not 1 <= priority <= 5 or max_attempts < 1:
            raise QueueError("bad job")
        if unique_key is not None:
            for job in self.jobs.values():
                if job.unique_key == unique_key and job.status in ("PENDING", "LEASED"):
                    return job
        job_id = next(self._ids)
        job = Job(job_id, name, priority, run_at or now, max_attempts, unique_key, job_id)
        self.jobs[job_id] = job
        return job

    def _ready(self, job, now):
        return job.status == "PENDING"

    def lease(self, worker, now):
        ready = [j for j in self.jobs.values() if self._ready(j, now)]
        if not ready:
            return None
        job = min(ready, key=lambda j: (-j.priority, j.seq))
        job.status, job.worker, job.lease_until = "LEASED", worker, now + LEASE
        return job

    def _held(self, job_id, worker, now):
        job = self.jobs.get(job_id)
        if job is None or job.status != "LEASED":
            raise QueueError("job is not leased")
        return job

    def complete(self, job_id, worker, now):
        job = self._held(job_id, worker, now)
        job.status, job.worker, job.lease_until = "DONE", None, None
        return job

    def fail(self, job_id, worker, now):
        job = self._held(job_id, worker, now)
        job.attempts += 1
        job.worker, job.lease_until = None, None
        if job.attempts >= job.max_attempts - 1:
            job.status = "DEAD"
        else:
            job.status = "PENDING"
            job.run_at = now + BASE_BACKOFF * (2 ** job.attempts)
        return job
