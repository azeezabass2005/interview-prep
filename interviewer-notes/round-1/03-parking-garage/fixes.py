FIXES = [
    ("garage/pricing.py", "    hours = -(-minutes // 60)  # started hours\n    return min(hours * HOURLY_CENTS, DAILY_MAX_CENTS)",
     "    full_days, rest = divmod(minutes, MINUTES_PER_DAY)\n"
     "    hours = -(-rest // 60)  # started hours\n"
     "    return full_days * DAILY_MAX_CENTS + min(hours * HOURLY_CENTS, DAILY_MAX_CENTS)"),
    ("garage/pricing.py", "    LOST_TICKET_CENTS,\n)", "    LOST_TICKET_CENTS,\n    MINUTES_PER_DAY,\n)"),
    ("garage/pricing.py", "if minutes < GRACE_MINUTES:", "if minutes <= GRACE_MINUTES:"),
    ("garage/pricing.py", "EARLY_BIRD_START_HOUR <= entry.hour <= EARLY_BIRD_END_HOUR", "EARLY_BIRD_START_HOUR <= entry.hour < EARLY_BIRD_END_HOUR"),
    ("garage/pricing.py", "        return EARLY_BIRD_CENTS\n", "        return min(EARLY_BIRD_CENTS, _hourly_with_cap(minutes))\n"),
    ("garage/tickets.py", "        ticket = self._tickets[ticket_id]\n",
     "        ticket = self._tickets[ticket_id]\n        if ticket.exited_at is not None:\n            raise ValueError(\"ticket already closed\")\n"),
    ("garage/pricing.py", "and exit.hour <= EARLY_BIRD_EXIT_BEFORE_HOUR", "and exit.hour < EARLY_BIRD_EXIT_BEFORE_HOUR"),
]
