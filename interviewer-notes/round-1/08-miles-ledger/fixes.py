FIXES = [
    ("miles.py", "        bonus = int(distance * BONUS[status])", "        bonus = int(base * BONUS[status])"),
    ("miles.py", "        return sum(e.miles for e in self._events(member) if e.kind == \"FLIGHT\"",
     "        return sum(e.base for e in self._events(member) if e.kind == \"FLIGHT\""),
    ("miles.py", "        return self._level(self._qualifying(member, on.year))",
     "        levels = [self._level(self._qualifying(member, year)) for year in (on.year, on.year - 1)]\n        return max(levels, key=RANK.index)"),
    ("miles.py", "ACTIVITY = (\"FLIGHT\",)", "ACTIVITY = (\"FLIGHT\", \"REDEEM\")"),
    ("miles.py", "        if miles > TRANSFER_LIMIT:",
     "        sent = -sum(e.miles for e in self._events(sender) if e.kind == \"TRANSFER_OUT\" and e.when.year == on.year)\n        if sent + miles > TRANSFER_LIMIT:"),
]
