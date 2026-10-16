from datetime import datetime
from decimal import Decimal

from ..config import LATE_PENALTY_PER_DAY, MAX_LATE_DAYS
from ..models import Assignment


def late_days(due: datetime, submitted_at: datetime) -> int:
    if submitted_at <= due:
        return 0
    return int((submitted_at - due).total_seconds() // 86400)


def penalised(assignment: Assignment, points: Decimal, submitted_at: datetime) -> Decimal:
    if assignment.category != "HOMEWORK":
        return points
    days = late_days(assignment.due, submitted_at)
    if days > MAX_LATE_DAYS:
        return Decimal(0)
    return max(Decimal(0), points - assignment.max_points * LATE_PENALTY_PER_DAY * days)
