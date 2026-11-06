from dataclasses import asdict

from ..errors import Forbidden
from ..http import Request, Response


class Handlers:
    def __init__(self, quotes, metrics):
        self._quotes = quotes
        self._metrics = metrics

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.get("/quotes", self.batch)
        router.get("/quotes/{symbol}", self.one)
        router.get("/instruments", self.search)
        router.get("/instruments/{symbol}/history", self.history)
        router.get("/internal/metrics", self.metrics)

    def one(self, request: Request) -> Response:
        return Response(200, asdict(self._quotes.quote(request.params["symbol"], request.query.get("ccy"))))

    def batch(self, request: Request) -> Response:
        quotes = self._quotes.quotes(request.query.get("symbols", "").split(","), request.query.get("ccy"))
        return Response(200, {"quotes": [asdict(q) for q in quotes]})

    def search(self, request: Request) -> Response:
        return Response(200, {"instruments": [asdict(i) for i in self._quotes.search(request.query.get("q", ""))]})

    def history(self, request: Request) -> Response:
        bars = self._quotes.history(request.params["symbol"], request.query.get("from", ""), request.query.get("to", ""))
        return Response(200, {"symbol": request.params["symbol"].upper(), "bars": [asdict(b) for b in bars]})

    def metrics(self, request: Request) -> Response:
        if not request.principal.has_role("ops"):
            raise Forbidden("ops only")
        series = [{"name": n, "labels": dict(l), "value": v} for (n, l), v in self._metrics.counters.items()]
        return Response(200, {"counters": series})
