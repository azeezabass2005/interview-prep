from ..http import Request, Response
from ..models import Trade


def trade_json(t: Trade, counterparty: str | None = None) -> dict:
    body = {"id": t.id, "desk": t.desk, "trader_id": t.trader_id, "counterparty_id": t.counterparty_id, "symbol": t.symbol,
            "side": t.side, "quantity": t.quantity, "price_cents": t.price_cents, "status": t.status,
            "trade_date": t.trade_date, "booked_at": t.booked_at, "version": t.version}
    if counterparty is not None:
        body["counterparty"] = counterparty
    return body


class Handlers:
    def __init__(self, trading, positions):
        self._trading = trading
        self._positions = positions

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.post("/trades", self.book)
        router.get("/trades/{trade_id}", self.get)
        router.patch("/trades/{trade_id}", self.amend)
        router.post("/trades/{trade_id}/cancel", self.cancel)
        router.get("/trades/{trade_id}/audit", self.audit)
        router.get("/blotter", self.blotter)
        router.get("/positions", self.positions)
        router.get("/snapshots/{business_date}", self.snapshot)

    def book(self, request: Request) -> Response:
        return Response(201, trade_json(self._trading.book(request.principal, request.json())))

    def get(self, request: Request) -> Response:
        return Response(200, trade_json(self._trading.get(request.principal, request.params["trade_id"])))

    def amend(self, request: Request) -> Response:
        data = request.json()
        trade = self._trading.amend(request.principal, request.params["trade_id"], data.get("quantity"),
                                    data.get("price_cents"))
        return Response(200, trade_json(trade))

    def cancel(self, request: Request) -> Response:
        return Response(200, trade_json(self._trading.cancel(request.principal, request.params["trade_id"])))

    def audit(self, request: Request) -> Response:
        return Response(200, {"entries": self._trading.audit(request.principal, request.params["trade_id"])})

    def blotter(self, request: Request) -> Response:
        rows = self._trading.blotter(request.principal, request.query.get("desk"), request.query.get("date"))
        return Response(200, {"trades": [trade_json(r["trade"], r["counterparty"]) for r in rows]})

    def positions(self, request: Request) -> Response:
        return Response(200, {"desk": request.principal.org_id, "positions": self._trading.positions(request.principal)})

    def snapshot(self, request: Request) -> Response:
        desk = request.principal.org_id
        return Response(200, {"desk": desk, "business_date": request.params["business_date"],
                              "positions": self._positions.snapshots(desk, request.params["business_date"])})
