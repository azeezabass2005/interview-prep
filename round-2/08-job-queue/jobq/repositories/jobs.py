import json
from datetime import datetime
from typing import List, Optional

from ..db import Database
from ..models import Job


def _dt(value):
    return datetime.fromisoformat(value) if value else None


def _to_job(r) -> Job:
    return Job(r["job_id"], r["kind"], json.loads(r["payload"]), r["status"], r["attempts"], r["max_attempts"],
               _dt(r["run_at"]), r["lease_owner"], _dt(r["claimed_at"]), _dt(r["lease_expires_at"]), r["last_error"])


class JobRepository:
    def __init__(self, db: Database):
        self._db = db

    def enqueue(self, kind: str, payload: dict, run_at: datetime, max_attempts: int) -> int:
        with self._db.transaction() as conn:
            cur = conn.execute("INSERT INTO jobs (kind, payload, run_at, max_attempts) VALUES (?, ?, ?, ?)",
                               (kind, json.dumps(payload), run_at.isoformat(), max_attempts))
            return cur.lastrowid

    def get(self, job_id: int) -> Optional[Job]:
        with self._db.transaction() as conn:
            r = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return _to_job(r) if r else None

    def next_candidate(self, now: datetime) -> Optional[Job]:
        with self._db.transaction() as conn:
            r = conn.execute(
                """SELECT * FROM jobs
                   WHERE (status = 'PENDING' AND run_at <= :now)
                      OR (status = 'RUNNING' AND lease_expires_at < :now)
                   ORDER BY run_at, job_id LIMIT 1""",
                {"now": now.isoformat()},
            ).fetchone()
        return _to_job(r) if r else None

    def claim(self, job: Job, worker: str, now: datetime, lease_until: datetime) -> bool:
        with self._db.transaction() as conn:
            cur = conn.execute(
                """UPDATE jobs SET status = 'RUNNING', attempts = attempts + 1, lease_owner = ?,
                                  claimed_at = ?, lease_expires_at = ?
                   WHERE job_id = ? AND status = ? AND attempts = ?""",
                (worker, now.isoformat(), lease_until.isoformat(), job.job_id, job.status, job.attempts),
            )
            if cur.rowcount == 1:
                conn.execute("INSERT INTO job_runs (job_id, worker, started) VALUES (?, ?, ?)",
                             (job.job_id, worker, now.isoformat()))
        return cur.rowcount == 1

    def extend_lease(self, job_id: int, worker: str, lease_until: datetime) -> bool:
        with self._db.transaction() as conn:
            cur = conn.execute("UPDATE jobs SET lease_expires_at = ? WHERE job_id = ? AND lease_owner = ? AND status = 'RUNNING'",
                               (lease_until.isoformat(), job_id, worker))
        return cur.rowcount == 1

    def complete(self, job_id: int, worker: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE jobs SET status = 'DONE', lease_expires_at = NULL WHERE job_id = ? AND lease_owner = ?",
                         (job_id, worker))

    def reschedule(self, job_id: int, run_at: datetime, error: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE jobs SET status = 'PENDING', run_at = ?, last_error = ?, lease_owner = NULL, "
                         "lease_expires_at = NULL WHERE job_id = ?", (run_at.isoformat(), error, job_id))

    def bury(self, job_id: int, error: str) -> None:
        with self._db.transaction() as conn:
            conn.execute("UPDATE jobs SET status = 'DEAD', last_error = ?, lease_expires_at = NULL WHERE job_id = ?",
                         (error, job_id))

    def dead(self) -> List[Job]:
        with self._db.transaction() as conn:
            rows = conn.execute("SELECT * FROM jobs WHERE status = 'DEAD' ORDER BY job_id").fetchall()
        return [_to_job(r) for r in rows]

    def run_count(self, job_id: int) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM job_runs WHERE job_id = ?", (job_id,)).fetchone()[0]
