from datetime import date

from utility.models import Reading


def reading(month, consumed, exported=0, year=2026):
    return Reading(date(year, month, 1), consumed, exported)
