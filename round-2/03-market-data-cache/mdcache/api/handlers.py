from dataclasses import dataclass, field
from datetime import datetime

from ..models import Quote
from ..services.consolidation import VenueBook, consolidate
from ..services.quotes import QuoteService, SymbolNotFound


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


def format_ts(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def quote_json(q: Quote) -> dict:
    return {"symbol": q.symbol, "bid": str(q.bid), "ask": str(q.ask), "last": str(q.last),
            "spread": str(q.spread), "updated_at": format_ts(q.timestamp), "stale": q.stale}


class MarketDataApi:
    def __init__(self, quotes: QuoteService, venues: VenueBook, clock):
        self._quotes = quotes
        self._venues = venues
        self._clock = clock

    def get_quote(self, symbol: str) -> Response:
        if not symbol.isalnum():
            return Response(400, {"error": "bad symbol"})
        try:
            return Response(200, quote_json(self._quotes.get_quote(symbol)))
        except SymbolNotFound:
            return Response(404, {"error": f"unknown symbol {symbol}"})

    def get_consolidated(self, symbol: str) -> Response:
        q = consolidate(symbol.upper(), self._venues.quotes_for(symbol.upper()), self._clock.time())
        if q is None:
            return Response(404, {"error": "no fresh venue quotes"})
        return Response(200, quote_json(q))
