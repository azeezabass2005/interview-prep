FIXES = [
    ("library/calendar.py", "        return d not in self.holidays", "        return d.weekday() != 6 and d not in self.holidays"),
    ("library/loans.py", "    return Loan(item_type, on, on + timedelta(days=LOAN_DAYS[item_type]))",
     "    return Loan(item_type, on, cal.next_open(on + timedelta(days=LOAN_DAYS[item_type])))"),
    ("library/loans.py", "    loan.due_on = cal.next_open(today + timedelta(days=LOAN_DAYS[loan.item_type]))",
     "    loan.due_on = cal.next_open(loan.due_on + timedelta(days=LOAN_DAYS[loan.item_type]))"),
    ("library/loans.py",
     "    if loan.item_type == \"BOOK\":\n        days_late = max(0, days_late - BOOK_GRACE_DAYS)\n"
     "    return days_late * DAILY_FINE[loan.item_type]",
     "    if loan.item_type == \"BOOK\" and days_late <= BOOK_GRACE_DAYS:\n        days_late = 0\n"
     "    return min(days_late * DAILY_FINE[loan.item_type], REPLACEMENT_COST[loan.item_type])"),
    ("library/account.py", "        return self.fines <= BLOCK_THRESHOLD", "        return self.fines < BLOCK_THRESHOLD"),
]
