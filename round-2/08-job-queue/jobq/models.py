from dataclasses import dataclass
from datetime import datetime
from typing import Optional

PENDING, RUNNING, DONE, DEAD = "PENDING", "RUNNING", "DONE", "DEAD"


@dataclass(frozen=True)
class Job:
    job_id: int
    kind: str
    payload: dict
    status: str
    attempts: int
    max_attempts: int
    run_at: datetime
    lease_owner: Optional[str]
    claimed_at: Optional[datetime]
    lease_expires_at: Optional[datetime]
    last_error: Optional[str]
