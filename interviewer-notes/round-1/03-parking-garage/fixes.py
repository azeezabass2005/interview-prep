FIXES = [
    ("garage/services/pricing.py", "    return min(started_hours(minutes) * HOURLY_CENTS, DAILY_MAX_CENTS)",
     "    full_days, rest = divmod(minutes, MINUTES_PER_DAY)\n"
     "    return full_days * DAILY_MAX_CENTS + min(started_hours(rest) * HOURLY_CENTS, DAILY_MAX_CENTS)"),
    ("garage/services/pricing.py", "LOST_TICKET_CENTS, VALIDATION_MINUTES)", "LOST_TICKET_CENTS, MINUTES_PER_DAY, VALIDATION_MINUTES)"),
    ("garage/services/pricing.py", "    if minutes < GRACE_MINUTES:", "    if minutes <= GRACE_MINUTES:"),
    ("garage/services/pricing.py", "EARLY_BIRD_FROM_HOUR <= entry.hour <= EARLY_BIRD_UNTIL_HOUR", "EARLY_BIRD_FROM_HOUR <= entry.hour < EARLY_BIRD_UNTIL_HOUR"),
    ("garage/services/occupancy.py",
     "            return counts[\"total\"] < PUBLIC_SPACES + RESERVED_SPACES\n        return counts[\"total\"] < PUBLIC_SPACES + RESERVED_SPACES",
     "            return counts[\"total\"] < PUBLIC_SPACES + RESERVED_SPACES\n        return counts[\"public\"] < PUBLIC_SPACES"),
    ("garage/services/gates.py", "if ticket.pass_holder and now.weekday() < 5 and not lost:",
     "if ticket.pass_holder and ticket.entered_at.weekday() < 5 and not lost:"),
]
