from datetime import date
from decimal import Decimal

from ..errors import PayrollError
from ..models import Worker


def rate_on(worker: Worker, day: date) -> Decimal:
    applicable = [r for r in worker.rates if r.effective <= day]
    if not applicable:
        raise PayrollError(f"{worker.worker_id} has no rate on {day}")
    latest = max(worker.rates, key=lambda r: r.effective)
    return latest.hourly
