from datetime import date

from .errors import LibraryError
from .services.circulation import CirculationService
from .store import InMemoryStore


class LibraryApi:
    def __init__(self, store: InMemoryStore, circulation: CirculationService):
        self._store = store
        self._c = circulation

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except LibraryError as exc:
            return exc.status, {"error": str(exc)}

    def setup(self, branches: dict, items: dict, patrons):
        for code, holidays in branches.items():
            self._c.add_branch(code, [date.fromisoformat(h) for h in holidays])
        for barcode, (kind, branch) in items.items():
            self._c.add_item(barcode, kind, branch)
        for p in patrons:
            self._c.add_patron(p)
        return 201, {}

    def checkout(self, patron, barcode, on):
        return self._call(lambda: {"due": self._c.checkout(patron, barcode, date.fromisoformat(on)).due_on.isoformat()}, 201)

    def hold(self, patron, barcode):
        return self._call(lambda: {"position": self._c.place_hold(patron, barcode)}, 201)

    def renew(self, barcode, today):
        return self._call(lambda: {"due": self._c.renew(barcode, date.fromisoformat(today)).due_on.isoformat()})

    def check_in(self, barcode, on):
        return self._call(lambda: {"fine": str(self._c.check_in(barcode, date.fromisoformat(on)).fine)})

    def patron(self, patron_id):
        p = self._store.patrons[patron_id]
        return 200, {"balance": str(p.balance), "loans": len(self._store.loans_for(patron_id))}
