FIXES = [
    ("studio.py", "        if name in c.booked:\n            raise StudioError(\"already booked\")",
     "        if name in c.booked or name in c.waitlist:\n            raise StudioError(\"already has a place\")"),
    ("studio.py", "        name = c.waitlist.pop()", "        name = c.waitlist.pop(0)"),
    ("studio.py", "        late = c.starts_at - self.clock.now() <= LATE_WINDOW", "        late = c.starts_at - self.clock.now() < LATE_WINDOW"),
    ("studio.py", "            m.fees += fee\n", "            m.fees += fee\n        if not late and m.plan == \"PACK\":\n            m.credits += 1\n"),
    ("studio.py", "        if not c.waitlist or len(c.booked) >= c.capacity:",
     "        if not c.waitlist or len(c.booked) >= c.capacity or c.starts_at - self.clock.now() < NO_PROMOTION:"),
]
