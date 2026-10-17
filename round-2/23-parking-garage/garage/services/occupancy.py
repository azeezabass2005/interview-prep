from ..config import PUBLIC_SPACES, RESERVED_SPACES
from ..store import InMemoryStore


class Occupancy:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def counts(self) -> dict:
        inside = self._store.inside()
        pass_count = sum(1 for t in inside if t.pass_holder)
        return {"public": len(inside) - pass_count, "pass": pass_count, "total": len(inside)}

    def can_admit(self, pass_holder: bool) -> bool:
        counts = self.counts()
        if pass_holder:
            return counts["total"] < PUBLIC_SPACES + RESERVED_SPACES
        return counts["total"] < PUBLIC_SPACES + RESERVED_SPACES
