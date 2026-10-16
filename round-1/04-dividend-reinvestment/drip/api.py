from datetime import date
from decimal import Decimal, InvalidOperation

from .errors import DripError, ValidationError
from .models import Account, DividendEvent, Movement
from .register import ShareRegister
from .services.enrolment import EnrolmentService
from .services.processor import DividendProcessor
from .store import InMemoryStore


class DripApi:
    def __init__(self, store: InMemoryStore, register: ShareRegister, enrolment: EnrolmentService,
                 processor: DividendProcessor):
        self._store = store
        self._register = register
        self._enrolment = enrolment
        self._processor = processor

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except DripError as exc:
            return exc.status, {"error": str(exc)}
        except (KeyError, ValueError, InvalidOperation) as exc:
            return 400, {"error": f"bad request: {exc}"}

    def open_account(self, body: dict):
        def go():
            self._store.add_account(Account(body["account_id"], body.get("name", ""), body["country"]))
            return {"account_id": body["account_id"]}
        return self._call(go, 201)

    def record_movement(self, body: dict):
        def go():
            if self._store.account(body["account_id"]) is None:
                raise ValidationError("unknown account")
            self._register.record(Movement(body["account_id"], body["security"], date.fromisoformat(body["on"]),
                                           Decimal(str(body["shares"])), body.get("reason", "TRADE")))
            return {"ok": True}
        return self._call(go, 201)

    def set_enrolment(self, body: dict):
        return self._call(lambda: {"enrolled": self._enrolment.set(body["account_id"], body["security"], body["enrolled"],
                                                                   date.fromisoformat(body["effective_from"])).enrolled})

    def declare(self, body: dict):
        def go():
            event = DividendEvent(body["event_id"], body["security"], date.fromisoformat(body["record_date"]),
                                  date.fromisoformat(body["pay_date"]), Decimal(str(body["per_share"])),
                                  Decimal(str(body["reinvest_price"])))
            if event.pay_date < event.record_date:
                raise ValidationError("pay date before record date")
            self._store.add_event(event)
            return {"event_id": event.event_id}
        return self._call(go, 201)

    def process(self, event_id: str):
        def go():
            return {"payments": [{"account_id": p.account_id, "gross": str(p.gross), "withholding": str(p.withholding),
                                  "fee": str(p.fee), "cash_paid": str(p.cash_paid), "shares_bought": str(p.shares_bought),
                                  "leftover": str(p.leftover)} for p in self._processor.process(event_id)]}
        return self._call(go)

    def holding(self, account_id: str, security: str, on: str):
        return self._call(lambda: {"shares": str(self._register.holding(account_id, security, date.fromisoformat(on)))})
