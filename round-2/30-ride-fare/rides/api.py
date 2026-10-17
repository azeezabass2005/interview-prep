from .errors import RideError
from .services.trips import TripService


class RideApi:
    def __init__(self, trips: TripService):
        self._trips = trips

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except RideError as exc:
            return exc.status, {"error": str(exc)}

    def request(self, body: dict):
        def go():
            t = self._trips.request(body["rider"], body["zone"], body.get("promo"))
            return {"trip_id": t.trip_id, "surge": str(t.locked_surge)}
        return self._call(go, 201)

    def assign(self, trip_id: str, driver: str, eta_seconds: int):
        return self._call(lambda: {"status": self._trips.assign(trip_id, driver, eta_seconds).status})

    def arrive(self, trip_id: str):
        return self._call(lambda: {"status": self._trips.arrive(trip_id).status})

    def pick_up(self, trip_id: str):
        return self._call(lambda: {"status": self._trips.pick_up(trip_id).status})

    def complete(self, trip_id: str, body: dict):
        def go():
            t = self._trips.complete(trip_id, body["miles"], body.get("tolls", "0"))
            return {"fare": str(t.fare), "driver_payout": str(t.driver_payout)}
        return self._call(go)

    def cancel(self, trip_id: str):
        return self._call(lambda: {"fee": str(self._trips.cancel(trip_id).cancel_fee)})
