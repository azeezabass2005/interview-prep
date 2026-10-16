from .errors import MeteringError
from .services.invoices import invoice
from .services.limiter import Limiter
from .store import InMemoryStore


class MeteringApi:
    def __init__(self, store: InMemoryStore, limiter: Limiter):
        self._store = store
        self._limiter = limiter

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except MeteringError as exc:
            return exc.status, {"error": str(exc)}

    def register(self, client_id: str, plan: str):
        return self._call(lambda: {"client_id": self._limiter.register(client_id, plan).client_id}, 201)

    def change_plan(self, client_id: str, plan: str):
        return self._call(lambda: {"plan": self._limiter.change_plan(client_id, plan).plan.name})

    def request(self, client_id: str, endpoint: str):
        def go():
            d = self._limiter.check(client_id, endpoint)
            return {"allowed": d.allowed, "retry_after": None if d.retry_after is None else str(d.retry_after),
                    "reason": d.reason}
        return self._call(go)

    def invoice(self, client_id: str, month: str):
        return self._call(lambda: invoice(self._store.client(client_id), month))
