from collections import Counter
from datetime import datetime, timedelta

from .repositories.requests import RequestRepository


def weekly_summary(requests: RequestRepository, week_start: datetime) -> dict:
    """Counts by status and average score for requests created in the week (Mon 00:00 to next Mon)."""
    week_end = week_start + timedelta(days=7)
    in_week = [r for r in requests.all() if week_start <= r.created_at < week_end]
    by_status = Counter(r.status for r in in_week)
    avg = round(sum(r.score for r in in_week) / len(in_week), 1) if in_week else 0.0
    top_senders = Counter(r.sender.lower() for r in in_week).most_common(3)
    return {"week_start": week_start.date().isoformat(), "total": len(in_week),
            "by_status": dict(by_status), "average_score": avg, "top_senders": top_senders}
