from datetime import date

from .errors import BillingError
from .models import Reading
from .services.billing import BillingService
from .store import InMemoryStore


def bill_json(b):
    return {"start": b.period_start.isoformat(), "end": b.period_end.isoformat(), "days": b.days,
            "imported": b.imported, "exported": b.exported, "billable_kwh": b.billable_kwh,
            "energy": str(b.energy), "tax": str(b.tax), "service": str(b.service), "total": str(b.total),
            "true_up_payout": str(b.true_up_payout)}


class UtilityApi:
    def __init__(self, store: InMemoryStore, billing: BillingService):
        self._store = store
        self._billing = billing

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except BillingError as exc:
            return exc.status, {"error": str(exc)}

    def open(self, body: dict):
        def go():
            first = Reading(date.fromisoformat(body["read_on"]), body["import"], body["export"])
            return {"account_id": self._billing.open_account(body["account_id"], body.get("address", ""), first).account_id}
        return self._call(go, 201)

    def read(self, account_id: str, body: dict):
        return self._call(lambda: bill_json(self._billing.read(
            account_id, Reading(date.fromisoformat(body["read_on"]), body["import"], body["export"]))), 201)

    def bank(self, account_id: str):
        return self._call(lambda: {"bank_kwh": self._store.account(account_id).bank_kwh})
