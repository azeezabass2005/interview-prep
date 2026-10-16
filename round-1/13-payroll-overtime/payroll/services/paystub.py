from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ..store import InMemoryStore
from .overtime import classify
from .timesheets import TimesheetService

WITHHOLDING = Decimal("0.10")
CENT = Decimal("0.01")


class PayrollService:
    def __init__(self, store: InMemoryStore, timesheets: TimesheetService):
        self._store = store
        self._timesheets = timesheets

    def stub(self, worker_id: str, monday: date) -> dict:
        rows = classify(self._timesheets.week(worker_id, monday))
        gross = Decimal(0)
        totals = {"regular": Decimal(0), "overtime": Decimal(0), "double": Decimal(0)}
        for day, regular, overtime, double in rows:
            gross += day.rate * (regular + overtime * Decimal("1.5") + double * 2)
            totals["regular"] += regular
            totals["overtime"] += overtime
            totals["double"] += double
        gross = gross.quantize(CENT, rounding=ROUND_HALF_UP)
        withholding = (gross * WITHHOLDING).quantize(CENT, rounding=ROUND_HALF_UP)
        return {"worker_id": worker_id, "week_of": monday.isoformat(),
                "hours": {k: str(v.quantize(CENT)) for k, v in totals.items()},
                "gross": str(gross), "withholding": str(withholding), "net": str(gross - withholding)}
