from datetime import datetime, timedelta
from typing import List

from ..config import BATCH_SIZE, MAX_DURATION_MINUTES, MIN_DURATION_MINUTES, URGENCY_WEIGHTS
from ..db import Database
from ..errors import ValidationError
from ..ids import new_id
from ..models import SCHEDULED, UNSCHEDULABLE, BatchResult, Meeting, MeetingRequest
from ..notifications import Notifier
from ..repositories.commitments import CommitmentRepository
from ..repositories.meetings import MeetingRepository
from ..repositories.requests import RequestRepository
from .availability import first_free_slot
from .scoring import ScoringService


class SchedulingService:
    def __init__(self, db: Database, clock, scoring: ScoringService = None, notifier: Notifier = None):
        self._clock = clock
        self._requests = RequestRepository(db)
        self._commitments = CommitmentRepository(db)
        self._meetings = MeetingRepository(db)
        self._scoring = scoring or ScoringService()
        self._notifier = notifier or Notifier(db, clock)


    def _validate(self, payload: dict) -> None:
        for field in ("title", "sender", "duration_minutes", "urgency", "earliest", "latest"):
            if field not in payload:
                raise ValidationError(f"missing field: {field}")
        duration = payload["duration_minutes"]
        if not isinstance(duration, int) or duration % 15 or not MIN_DURATION_MINUTES <= duration <= MAX_DURATION_MINUTES:
            raise ValidationError("duration_minutes must be 15-120 in steps of 15")
        if payload["urgency"] not in URGENCY_WEIGHTS:
            raise ValidationError("urgency must be low, normal or high")
        if datetime.fromisoformat(payload["latest"]) <= datetime.fromisoformat(payload["earliest"]):
            raise ValidationError("latest must be after earliest")

    def submit_request(self, requester: str, idempotency_key: str, payload: dict) -> MeetingRequest:
        self._validate(payload)

        existing = self._requests.find_by_key(requester, idempotency_key)
        if existing is not None:
            return existing

        req = MeetingRequest(
            request_id=new_id("req"),
            requester=requester,
            idempotency_key=idempotency_key,
            title=payload["title"],
            sender=payload["sender"],
            duration_minutes=payload["duration_minutes"],
            urgency=payload["urgency"],
            earliest=datetime.fromisoformat(payload["earliest"]),
            latest=datetime.fromisoformat(payload["latest"]),
            created_at=self._clock.now(),
            score=self._scoring.score(payload["sender"], payload["urgency"]),
        )
        self._requests.insert(req)
        self._notifier.request_received(req)
        return req

    def get_request(self, request_id: str):
        return self._requests.get(request_id)


    def run_batch(self, day: datetime) -> BatchResult:
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        pending = self._requests.pending_for_day(day_start, day_end)

        scheduled: List[str] = []
        unschedulable = 0
        for i in range(0, len(pending), BATCH_SIZE):
            chunk = pending[i:i + BATCH_SIZE - 1]
            for req in chunk:
                meeting = self._place(day_start, req)
                if meeting is None:
                    self._requests.set_status(req.request_id, UNSCHEDULABLE)
                    unschedulable += 1
                else:
                    scheduled.append(meeting.meeting_id)
        return BatchResult(day_start.date().isoformat(), len(scheduled), unschedulable, tuple(scheduled))

    def _place(self, day_start: datetime, req: MeetingRequest):
        day_end = day_start + timedelta(days=1)
        busy = [(c.start, c.end) for c in self._commitments.between(day_start, day_end) if c.protected]
        busy += [(m.start, m.end) for m in self._meetings.between(day_start, day_end)]
        slot = first_free_slot(day_start, req.earliest, req.latest, timedelta(minutes=req.duration_minutes), busy)
        if slot is None:
            return None
        meeting = Meeting(new_id("mtg"), req.request_id, req.title, slot[0], slot[1])
        self._meetings.add(meeting)
        self._requests.set_status(req.request_id, SCHEDULED)
        self._notifier.request_scheduled(req, slot[0])
        return meeting

    def schedule_for(self, day: datetime):
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        return self._commitments.between(day_start, day_end), self._meetings.between(day_start, day_end)
