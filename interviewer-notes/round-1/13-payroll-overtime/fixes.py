FIXES = [
    ("payroll/hours.py",
     "        hours = Decimal(int((shift.end - shift.start).total_seconds() // 3600))\n        totals[shift.end.date()] += hours",
     "        hours = Decimal(int((shift.end - shift.start).total_seconds())) / 3600\n        totals[shift.start.date()] += hours"),
    ("payroll/overtime.py",
     """    for day, hours in sorted(day_hours.items()):
        regular += min(hours, DAILY_REGULAR)
        overtime += max(hours - DAILY_REGULAR, ZERO)
        double += max(hours - DAILY_DOUBLE_AFTER, ZERO)

    total = sum(day_hours.values(), ZERO)
    weekly_overtime = max(total - WEEKLY_REGULAR, ZERO)""",
     """    worked_days = [d for d, h in sorted(day_hours.items()) if h > 0]
    seventh_day = worked_days[6] if len(worked_days) == 7 else None
    for day, hours in sorted(day_hours.items()):
        if day == seventh_day:
            overtime += min(hours, DAILY_REGULAR)
            double += max(hours - DAILY_REGULAR, ZERO)
            continue
        regular += min(hours, DAILY_REGULAR)
        overtime += max(min(hours, DAILY_DOUBLE_AFTER) - DAILY_REGULAR, ZERO)
        double += max(hours - DAILY_DOUBLE_AFTER, ZERO)

    weekly_overtime = max(regular - WEEKLY_REGULAR, ZERO)"""),
]
