FIXES = [
    ("library/services/calendar.py", "    return d not in branch.holidays", "    return d.weekday() != 6 and d not in branch.holidays"),
    ("library/services/fines.py", "    if loan.kind == \"BOOK\":\n        days = max(0, days - BOOK_GRACE_DAYS)",
     "    if loan.kind == \"BOOK\" and days <= BOOK_GRACE_DAYS:\n        days = 0"),
    ("library/services/circulation.py", "next_open(branch, today + timedelta(days=LOAN_DAYS[loan.kind]))",
     "next_open(branch, loan.due_on + timedelta(days=LOAN_DAYS[loan.kind]))"),
    ("library/services/circulation.py", "        if loan.renewals >= MAX_RENEWALS:",
     "        if self._item(barcode).holds:\n            raise Refused(\"someone is waiting for this item\")\n        if loan.renewals >= MAX_RENEWALS:"),
    ("library/services/circulation.py", "if patron.balance > BLOCK_AT:", "if patron.balance >= BLOCK_AT:"),
]
