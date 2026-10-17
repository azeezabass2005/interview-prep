FIXES = [
    ("meetings.py", "        if request_id in self.by_request:\n            return self.meetings[self.by_request[request_id]]",
     "        if (organizer, request_id) in self.by_request:\n            return self.meetings[self.by_request[(organizer, request_id)]]"),
    ("meetings.py", "        self.by_request[request_id] = meeting.meeting_id", "        self.by_request[(organizer, request_id)] = meeting.meeting_id"),
    ("meetings.py", "        return a_start <= b_end and b_start <= a_end", "        return a_start < b_end and b_start < a_end"),
    ("meetings.py", "        local_start = start.astimezone(timezone.utc)\n        local_end = end.astimezone(timezone.utc)",
     "        local_start = start.astimezone(self.users[user])\n        local_end = end.astimezone(self.users[user])"),
    ("meetings.py", "self._conflicts(tuple(attendees), start, end)", "self._conflicts(people, start, end)"),
    ("meetings.py", "        meeting.status = \"CANCELLED\"\n        return meeting",
     "        meeting.status = \"CANCELLED\"\n"
     "        for m in sorted(self.meetings.values(), key=lambda m: m.meeting_id):\n"
     "            if m.status == \"PENDING\" and not self._conflicts(m.participants, m.start, m.end, ignore=m.meeting_id):\n"
     "                m.status = \"CONFIRMED\"\n"
     "        return meeting"),
]
