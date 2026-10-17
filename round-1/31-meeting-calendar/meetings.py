import itertools
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Tuple
from zoneinfo import ZoneInfo

WORK_START = time(9, 0)
WORK_END = time(17, 0)
SLOT_MINUTES = 15
MAX_MINUTES = 240


class CalendarError(Exception):
    pass


@dataclass
class Meeting:
    meeting_id: int
    organizer: str
    attendees: Tuple[str, ...]
    start: datetime
    end: datetime
    status: str

    @property
    def participants(self):
        return (self.organizer,) + self.attendees


class Calendar:
    def __init__(self):
        self.users = {}
        self.meetings = {}
        self.by_request = {}
        self._ids = itertools.count(1)

    def add_user(self, name, tz):
        self.users[name] = ZoneInfo(tz)

    def _within_hours(self, user, start, end):
        local_start = start.astimezone(timezone.utc)
        local_end = end.astimezone(timezone.utc)
        return (local_start.weekday() < 5 and local_start.date() == local_end.date()
                and WORK_START <= local_start.time() and local_end.time() <= WORK_END)

    @staticmethod
    def _overlaps(a_start, a_end, b_start, b_end):
        return a_start <= b_end and b_start <= a_end

    def _conflicts(self, people, start, end, ignore=None):
        for m in self.meetings.values():
            if m.status != "CONFIRMED" or m.meeting_id == ignore:
                continue
            if set(people) & set(m.participants) and self._overlaps(start, end, m.start, m.end):
                return True
        return False

    def request(self, organizer, attendees, start, minutes, request_id):
        if request_id in self.by_request:
            return self.meetings[self.by_request[request_id]]
        if minutes < SLOT_MINUTES or minutes > MAX_MINUTES or minutes % SLOT_MINUTES:
            raise CalendarError("bad duration")
        people = (organizer,) + tuple(attendees)
        if any(p not in self.users for p in people) or len(set(people)) != len(people):
            raise CalendarError("bad participants")
        end = start + timedelta(minutes=minutes)
        for p in people:
            if not self._within_hours(p, start, end):
                raise CalendarError(f"outside {p}'s working hours")
        status = "PENDING" if self._conflicts(tuple(attendees), start, end) else "CONFIRMED"
        meeting = Meeting(next(self._ids), organizer, tuple(attendees), start, end, status)
        self.meetings[meeting.meeting_id] = meeting
        self.by_request[request_id] = meeting.meeting_id
        return meeting

    def cancel(self, meeting_id):
        meeting = self.meetings.get(meeting_id)
        if meeting is None or meeting.status == "CANCELLED":
            raise CalendarError("no such meeting")
        meeting.status = "CANCELLED"
        return meeting
