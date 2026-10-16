from datetime import date

from .errors import LoyaltyError
from .models import Member
from .services.flights import FlightService
from .services.ledger import Ledger
from .services.status import StatusService
from .services.transfers import TransferService
from .store import InMemoryStore


class LoyaltyApi:
    def __init__(self, store: InMemoryStore, status: StatusService, ledger: Ledger, flights: FlightService,
                 transfers: TransferService):
        self._store = store
        self._status = status
        self._ledger = ledger
        self._flights = flights
        self._transfers = transfers

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except LoyaltyError as exc:
            return exc.status, {"error": str(exc)}
        except ValueError as exc:
            return 400, {"error": str(exc)}

    def join(self, member_id: str, name: str):
        def go():
            self._store.add_member(Member(member_id, name))
            return {"member_id": member_id}
        return self._call(go, 201)

    def fly(self, body: dict):
        def go():
            f = self._flights.record(body["flight_id"], body["member_id"], date.fromisoformat(body["date"]), body["fare"])
            return {"base_miles": f.base_miles, "bonus_miles": f.bonus_miles}
        return self._call(go, 201)

    def cancel_flight(self, flight_id: str):
        return self._call(lambda: {"cancelled": self._flights.cancel(flight_id).cancelled})

    def redeem(self, member_id: str, miles: int, on: str):
        def go():
            self._ledger.spend(member_id, miles, date.fromisoformat(on))
            return {"balance": self._ledger.balance(member_id, date.fromisoformat(on))}
        return self._call(go)

    def transfer(self, body: dict):
        def go():
            self._transfers.transfer(body["from"], body["to"], int(body["miles"]), date.fromisoformat(body["date"]))
            return {"ok": True}
        return self._call(go)

    def account(self, member_id: str, on: str):
        d = date.fromisoformat(on)
        return self._call(lambda: {"balance": self._ledger.balance(member_id, d), "tier": self._status.tier(member_id, d)})
