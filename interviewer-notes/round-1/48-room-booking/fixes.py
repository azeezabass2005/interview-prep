FIXES = [
    ("rooms.py", "        return True", "        return b.checked_in or now < b.start + CHECK_IN_WINDOW"),
    ("rooms.py", "        if end <= start or end - start >= MAX_LENGTH:", "        if end <= start or end - start > MAX_LENGTH:"),
    ("rooms.py", "        local_start, local_end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)",
     "        tz = self.rooms[room].tz\n        local_start, local_end = start.astimezone(tz), end.astimezone(tz)"),
    ("rooms.py", "        created = []\n        for week in range(weeks):\n            shift = timedelta(weeks=week)\n            created.append(self.book(room, start + shift, end + shift, organizer, now))\n        return created",
     "        slots = [(start + timedelta(weeks=w), end + timedelta(weeks=w)) for w in range(weeks)]\n"
     "        for s, e in slots:\n            self._validate(room, s, e)\n            if not self._free(room, s, e, now):\n                raise BookingError(\"room is taken\")\n"
     "        return [self.book(room, s, e, organizer, now) for s, e in slots]"),
    ("rooms.py", "if r.capacity > attendees and", "if r.capacity >= attendees and"),
]
