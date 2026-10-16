from .errors import IpoError
from .reporting import allocation_report
from .services.book import BookService
from .services.closing import ClosingService


class IpoApi:
    def __init__(self, book: BookService, closing: ClosingService):
        self._book = book
        self._closing = closing

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except IpoError as exc:
            return exc.status, {"error": str(exc)}

    def create(self, offering_id: str, shares: int):
        return self._call(lambda: {"offering_id": self._book.create(offering_id, shares).offering_id}, 201)

    def submit(self, offering_id: str, body: dict):
        return self._call(lambda: {"seq": self._book.submit(offering_id, body["investor"], body["shares"], body["limit"]).seq}, 201)

    def amend(self, offering_id: str, body: dict):
        return self._call(lambda: {"shares": self._book.amend(offering_id, body["investor"], body.get("shares"),
                                                              body.get("limit")).shares})

    def cancel(self, offering_id: str, investor: str):
        return self._call(lambda: {"status": self._book.cancel(offering_id, investor).status})

    def close(self, offering_id: str, price):
        def go():
            offering = self._closing.close(offering_id, price)
            return {"allocations": dict(sorted(offering.allocations.items())), "report": allocation_report(offering)}
        return self._call(go)
