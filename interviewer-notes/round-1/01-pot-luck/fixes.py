FIXES = [
    ("potluck.py", "        return str(self.rng.randint(0, 99999))", "        return f\"{self.rng.randint(0, 99999):05d}\""),
    ("potluck.py", "        return len(set(code) & set(winning))", "        return sum(a == b for a, b in zip(code, winning))"),
    ("potluck.py", "            amount = draw.pot * share", "            amount = min(draw.pot * share, remaining)"),
    ("potluck.py", "if e.participant == participant_id)", "if e.participant == participant_id and e.active)"),
    ("potluck.py", "from decimal import ROUND_HALF_UP, Decimal", "from decimal import ROUND_DOWN, Decimal"),
    ("potluck.py", "rounding=ROUND_HALF_UP)", "rounding=ROUND_DOWN)"),
]
