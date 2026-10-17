from datetime import date, datetime
from decimal import Decimal

from .errors import PayrollError
from .models import RateChange, Worker
from .services.paystub import PayrollService
from .services.timesheets import TimesheetService
from .store import InMemoryStore


class PayrollApi:
    def __init__(self, store: InMemoryStore, timesheets: TimesheetService, payroll: PayrollService):
        self._store = store
        self._timesheets = timesheets
        self._payroll = payroll

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except PayrollError as exc:
            return exc.status, {"error": str(exc)}

    def hire(self, worker_id: str, name: str, rate, effective: str):
        def go():
            self._store.workers[worker_id] = Worker(worker_id, name, [RateChange(date.fromisoformat(effective), Decimal(str(rate)))])
            return {"worker_id": worker_id}
        return self._call(go, 201)

    def change_rate(self, worker_id: str, rate, effective: str):
        def go():
            self._store.worker(worker_id).rates.append(RateChange(date.fromisoformat(effective), Decimal(str(rate))))
            return {"ok": True}
        return self._call(go)

    def clock(self, worker_id: str, body: dict):
        return self._call(lambda: {"ok": bool(self._timesheets.record(
            worker_id, datetime.fromisoformat(body["start"]), datetime.fromisoformat(body["end"]),
            body.get("break_taken", False)))}, 201)

    def stub(self, worker_id: str, monday: str):
        return self._call(lambda: self._payroll.stub(worker_id, date.fromisoformat(monday)))
