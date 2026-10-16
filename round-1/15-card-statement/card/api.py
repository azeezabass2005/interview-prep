from datetime import date

from .errors import CardError
from .services.cycle import CycleService
from .services.posting import PostingService


class CardApi:
    def __init__(self, posting: PostingService, cycles: CycleService):
        self._posting = posting
        self._cycles = cycles

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except CardError as exc:
            return exc.status, {"error": str(exc)}

    def open(self, account_id: str, limit, opened_on: str):
        return self._call(lambda: {"account_id": self._posting.open(account_id, limit, date.fromisoformat(opened_on)).account_id}, 201)

    def post(self, account_id: str, body: dict):
        return self._call(lambda: {"kind": self._posting.post(account_id, date.fromisoformat(body["date"]), body["kind"],
                                                              body["amount"]).kind}, 201)

    def close(self, account_id: str, close_date: str):
        def go():
            s = self._cycles.close(account_id, date.fromisoformat(close_date))
            return {"days": s.days, "interest": {k: str(v) for k, v in s.interest.items()}, "fees": str(s.fees),
                    "balances": {k: str(v) for k, v in s.balances.items()}, "new_balance": str(s.new_balance),
                    "minimum_due": str(s.minimum_due), "due_date": s.due_date.isoformat()}
        return self._call(go)
