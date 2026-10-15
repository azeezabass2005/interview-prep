FIXES = [
    ("rooms/repositories/bookings.py",
     "    def starting_between(self, room_id: str, start: datetime, end: datetime) -> List[Booking]:",
     """    def insert_if_free(self, room_id: str, organizer: str, attendees, start: datetime, end: datetime,
                       series_id: Optional[str] = None) -> Optional[int]:
        \"\"\"Check for overlaps and insert under one write lock. None if the slot is taken.\"\"\"
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            clash = conn.execute("SELECT 1 FROM bookings WHERE room_id = ? AND start < ? AND end > ?",
                                 (room_id, end.isoformat(), start.isoformat())).fetchone()
            if clash:
                return None
            cur = conn.execute(
                "INSERT INTO bookings (room_id, organizer, attendees, start, end, series_id) VALUES (?, ?, ?, ?, ?, ?)",
                (room_id, organizer, ",".join(attendees), start.isoformat(), end.isoformat(), series_id))
            return cur.lastrowid

    def starting_between(self, room_id: str, start: datetime, end: datetime) -> List[Booking]:"""),
    ("rooms/services/booking.py",
     "        if self._bookings.overlapping(room_id, start, end):\n            raise Conflict(\"room is already booked\")\n"
     "        return self._bookings.insert(room_id, organizer, attendees, start, end, series_id)",
     "        if self._bookings.overlapping(room_id, start, end):\n            raise Conflict(\"room is already booked\")\n"
     "        booking_id = self._bookings.insert_if_free(room_id, organizer, attendees, start, end, series_id)\n"
     "        if booking_id is None:\n            raise Conflict(\"room is already booked\")\n        return booking_id"),
    ("rooms/services/booking.py", "        while start.date() < until and", "        while start.date() <= until and"),
    ("rooms/services/booking.py", "        if len(attendees) > room.capacity:",
     "        if len(set(attendees) | {organizer}) > room.capacity:"),
    ("rooms/services/booking.py", "    def _validate(self, room_id: str, attendees: Sequence[str], start: datetime, end: datetime):",
     "    def _validate(self, room_id: str, organizer: str, attendees: Sequence[str], start: datetime, end: datetime):"),
    ("rooms/services/booking.py", "        self._validate(room_id, attendees, start, end)",
     "        self._validate(room_id, organizer, attendees, start, end)"),
    ("rooms/services/availability.py", "from datetime import date, datetime, time, timedelta",
     "from datetime import date, datetime, time, timedelta, timezone\nfrom zoneinfo import ZoneInfo"),
    ("rooms/services/availability.py",
     "        day_start = datetime.combine(local_day, time.min)\n"
     "        return self._bookings.starting_between(room_id, day_start, day_start + timedelta(days=1))",
     "        tz = ZoneInfo(room.timezone)\n"
     "        to_utc = lambda d: datetime.combine(d, time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)\n"
     "        return self._bookings.starting_between(room_id, to_utc(local_day), to_utc(local_day + timedelta(days=1)))"),
]
