from dataclasses import dataclass
from datetime import datetime
from typing import Optional

PENDING = "PENDING"
SCHEDULED = "SCHEDULED"
UNSCHEDULABLE = "UNSCHEDULABLE"


@dataclass
class MeetingRequest:
    request_id: str
    requester: str
    idempotency_key: str
    title: str
    sender: str
    duration_minutes: int
    urgency: str
    earliest: datetime
    latest: datetime
    created_at: datetime
    score: int = 0
    status: str = PENDING


@dataclass(frozen=True)
class Commitment:
    commitment_id: str
    title: str
    start: datetime
    end: datetime
    protected: bool = True


@dataclass(frozen=True)
class Meeting:
    meeting_id: str
    request_id: str
    title: str
    start: datetime
    end: datetime


@dataclass(frozen=True)
class BatchResult:
    day: str
    scheduled: int
    unschedulable: int
    meeting_ids: tuple = ()
    note: Optional[str] = None
