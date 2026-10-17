from .engine import MatchingEngine
from .errors import ExchangeError
from .models import Order
from .validation import validate


class ExchangeApi:
    def __init__(self, engine: MatchingEngine):
        # Connect the API facade to its matching engine.
        self._engine = engine

    def _call(self, fn, ok=200):
        # Run an operation and translate exchange errors into API responses.
        try:
            return ok, fn()
        except ExchangeError as exc:
            return exc.status, {"error": str(exc)}

    def submit(self, member: str, body: dict):
        # Submit a member's order and return its execution results.
        def go():
            # Validate the request, submit the order, and serialize its trades.
            data = validate(body)
            order = Order(body["order_id"], member, data["symbol"], data["side"], data["price"], data["quantity"],
                          data["order_type"])
            trades = self._engine.submit(order)
            return {"status": order.status, "filled": order.filled,
                    "trades": [{"buy": t.buy_order, "sell": t.sell_order, "price": t.price, "quantity": t.quantity}
                               for t in trades]}
        return self._call(go, 201)

    def cancel(self, order_id: str):
        # Cancel an order and return its updated status.
        return self._call(lambda: {"status": self._engine.cancel(order_id).status})

    def amend(self, order_id: str, body: dict):
        # Amend an order and return its updated price and quantity.
        def go():
            # Apply the requested changes and serialize the amended order.
            o = self._engine.amend(order_id, body.get("price"), body.get("quantity"))
            return {"price": o.price, "quantity": o.quantity}
        return self._call(go)

    def depth(self, symbol: str, levels: int = 5):
        # Return aggregated bid and ask quantities for the requested price levels.
        book = self._engine.book(symbol.upper())
        return 200, {"bids": book.bids.depth(levels), "asks": book.asks.depth(levels)}

    def stats(self, symbol: str):
        # Return the symbol's last traded price and volume-weighted average price.
        tape = self._engine.tape
        vwap = tape.vwap(symbol.upper())
        return 200, {"last": tape.last_price(symbol.upper()), "vwap": str(vwap) if vwap is not None else None}
