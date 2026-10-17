FIXES = [
    ("garage.py", "        if minutes < FREE_MINUTES:", "        if minutes <= FREE_MINUTES:"),
    ("garage.py", "        if validated:\n            total -= HOURLY * VALIDATION_HOURS\n", ""),
    ("garage.py", "        days, rest = divmod(minutes, DAY_MINUTES)",
     "        if validated:\n            minutes = max(0, minutes - VALIDATION_HOURS * 60)\n        days, rest = divmod(minutes, DAY_MINUTES)"),
    ("garage.py", "        total = min(HOURLY * (days * 24 + hours), DAILY_MAX)",
     "        total = days * DAILY_MAX + min(HOURLY * hours, DAILY_MAX)"),
    ("garage.py", "        ticket.validations += 1", "        if ticket.validations:\n            raise GarageError(\"already validated\")\n        ticket.validations += 1"),
    ("garage.py", "            raise GarageError(\"garage full\")",
     "            raise GarageError(\"garage full\")\n        if not permit and len(self.inside) >= self.capacity - self.reserved:\n            raise GarageError(\"no visitor spaces\")"),
]
