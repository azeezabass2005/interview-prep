FIXES = [
    ("loyalty/services/earning.py", "    bonus = int(base * TIER_MULTIPLIER[tier]) if tier != \"BASE\" else 0",
     "    bonus = int(base * (TIER_MULTIPLIER[tier] - 1))"),
    ("loyalty/services/flights.py", "        self._store.add_qualifying(member_id, flown_on.year, base + bonus)",
     "        self._store.add_qualifying(member_id, flown_on.year, base)"),
    ("loyalty/services/flights.py", "-(flight.base_miles + flight.bonus_miles))", "-flight.base_miles)"),
    ("loyalty/services/ledger.py", "key=lambda l: (l.dated, l.lot_id), reverse=True):", "key=lambda l: (l.dated, l.lot_id)):"),
    ("loyalty/services/ledger.py", "        return platinum or on <= anniversary(lot.dated, EXPIRY_YEARS)",
     "        return platinum or on < anniversary(lot.dated, EXPIRY_YEARS)"),
    ("loyalty/services/transfers.py", "        self._store.add_qualifying(receiver, on.year, miles)\n", ""),
]
