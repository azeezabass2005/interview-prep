FIXES = [
    ("library.py", "        return start + timedelta(days=LOAN_DAYS[kind])",
     "        due = start + timedelta(days=LOAN_DAYS[kind])\n        return due + timedelta(days=1) if due.weekday() == SUNDAY else due"),
    ("library.py", "        fine = days_late * DAILY_FINE[kind]", "        fine = min(days_late * DAILY_FINE[kind], MAX_FINE[kind])"),
    ("library.py", "        loan.due = self._due(on, \"BOOK\")", "        loan.due = self._due(loan.due, \"BOOK\")"),
    ("library.py", "self.holds[item].pop()", "self.holds[item].pop(0)"),
    ("library.py", "if l.patron == patron) >= MAX_ITEMS:", "if l.patron == patron and l.returned is None) >= MAX_ITEMS:"),
]
