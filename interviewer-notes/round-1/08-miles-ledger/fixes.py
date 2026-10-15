FIXES = [
    ("miles/earning.py", "base = int(fare * MILES_PER_DOLLAR)", "base = int(fare) * MILES_PER_DOLLAR"),
    ("miles/earning.py", "bonus = int(base * TIER_MULTIPLIER[tier])", "bonus = int(base * (TIER_MULTIPLIER[tier] - 1))"),
    ("miles/account.py", "return lot.remaining > 0 and as_of <= self.expires_on(lot)",
     "if lot.remaining <= 0:\n            return False\n"
     "        return self.member.tier == \"PLATINUM\" or as_of < self.expires_on(lot)"),
    ("miles/account.py", "key=lambda l: l.earned_on, reverse=True)", "key=lambda l: l.earned_on)"),
    ("miles/account.py", "        usable = sorted(",
     "        if self.balance(on) < miles:\n            raise InsufficientMiles(f\"short by {miles - self.balance(on)} miles\")\n        usable = sorted("),
]
