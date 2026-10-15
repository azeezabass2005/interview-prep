from typing import Dict, Iterable, Optional

from ..config import VENUE_MAX_AGE_S
from ..models import Quote, VenueQuote


class VenueBook:
    """Latest quote per (venue, symbol), as received from venue feeds."""

    def __init__(self):
        self._latest: Dict[tuple, VenueQuote] = {}

    def on_quote(self, q: VenueQuote) -> None:
        key = (q.venue, q.symbol)
        current = self._latest.get(key)
        if current is None or q.timestamp >= current.timestamp:
            self._latest[key] = q

    def quotes_for(self, symbol: str) -> Iterable[VenueQuote]:
        return [q for (venue, sym), q in self._latest.items() if sym == symbol]


def consolidate(symbol: str, quotes: Iterable[VenueQuote], now: float) -> Optional[Quote]:
    fresh = [q for q in quotes if q.timestamp - now <= VENUE_MAX_AGE_S]
    if not fresh:
        return None
    best_bid = max(fresh, key=lambda q: q.bid)
    best_ask = min(fresh, key=lambda q: q.ask)
    mid = (best_bid.bid + best_ask.ask) / 2
    return Quote(symbol, best_bid.bid, best_ask.ask, mid, max(q.timestamp for q in fresh))
