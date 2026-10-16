import os
import tempfile
from datetime import datetime

from blike.api.handlers import CalendarApi
from blike.clock import FixedClock
from blike.db import Database
from blike.services.scheduling import SchedulingService

MONDAY = datetime(2026, 5, 4)
TUESDAY = datetime(2026, 5, 5)


class TempDb:

    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "calendar.db"))
        self.db.initialize()

    def cleanup(self):
        self._dir.cleanup()


def make_service(tmp: TempDb, now=datetime(2026, 5, 1, 9, 0)) -> SchedulingService:
    return SchedulingService(tmp.db, FixedClock(now))


def make_api(tmp: TempDb) -> CalendarApi:
    return CalendarApi(make_service(tmp))


def payload(title="Sync", sender="alex@bloomberg.example", duration=30, urgency="normal",
            earliest="2026-05-05T09:00", latest="2026-05-05T18:00"):
    return {"title": title, "sender": sender, "duration_minutes": duration, "urgency": urgency,
            "earliest": earliest, "latest": latest}


def headers(requester="ea-app", key="key-1"):
    return {"X-Requester": requester, "Idempotency-Key": key}
