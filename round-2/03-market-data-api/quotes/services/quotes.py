from datetime import date

from ..cache import TTLCache
from ..config import FX_TTL_SECONDS, MAX_BATCH, MAX_HISTORY_DAYS, QUOTE_TTL_MS
from ..errors import NotFound, ValidationError
from ..models import Bar, Instrument, Quote

SUPPORTED_CCY = {"USD", "EUR", "GBP", "JPY", "CHF"}


class QuoteService:
    def __init__(self, instruments, bars, vendor, clock):
        self._instruments = instruments
        self._bars = bars
        self._vendor = vendor
        self._quotes = TTLCache(clock, QUOTE_TTL_MS)
        self._fx = TTLCache(clock, FX_TTL_SECONDS)

    def _instrument(self, symbol: str) -> Instrument:
        instrument = self._instruments.get(symbol.upper())
        if instrument is None:
            raise NotFound(f"unknown symbol {symbol}")
        return instrument

    def _fx_rate(self, base: str, quote: str) -> float:
        if base == quote:
            return 1.0
        key = f"{base}{quote}"
        rate = self._fx.get(key)
        if rate is None:
            rate = self._vendor.fx_rate(base, quote)
            self._fx.set(key, rate)
        return rate

    def _latest(self, symbols: list[str]) -> dict[str, Quote]:
        found = {s: self._quotes.get(s) for s in symbols}
        missing = [s for s, q in found.items() if q is None]
        if missing:
            for symbol, raw in self._vendor.latest(missing).items():
                quote = Quote(symbol, float(raw["price"]), raw["currency"], raw["ts"])
                self._quotes.set(symbol, quote)
                found[symbol] = quote
        return {s: q for s, q in found.items() if q is not None}

    def _convert(self, quote: Quote, currency: str | None) -> Quote:
        if currency is None or currency == quote.currency:
            return quote
        if currency not in SUPPORTED_CCY:
            raise ValidationError(f"unsupported currency {currency}")
        rate = self._fx_rate(quote.currency, currency)
        quote.price = round(quote.price * rate, 4)
        quote.currency = currency
        return quote

    def quote(self, symbol: str, currency: str | None = None) -> Quote:
        instrument = self._instrument(symbol)
        latest = self._latest([instrument.symbol])
        if instrument.symbol not in latest:
            raise NotFound(f"no price for {symbol}")
        return self._convert(latest[instrument.symbol], currency)

    def quotes(self, symbols: list[str], currency: str | None = None) -> list[Quote]:
        symbols = [s.strip().upper() for s in symbols if s.strip()]
        if not 1 <= len(symbols) <= MAX_BATCH:
            raise ValidationError(f"between 1 and {MAX_BATCH} symbols")
        known = [self._instrument(s).symbol for s in symbols]
        latest = self._latest(known)
        return [self._convert(latest[s], currency) for s in known if s in latest]

    def search(self, text: str) -> list[Instrument]:
        text = text.strip()
        if len(text) < 2:
            raise ValidationError("search needs at least 2 characters")
        return self._instruments.search(text)

    def history(self, symbol: str, start: str, end: str) -> list[Bar]:
        instrument = self._instrument(symbol)
        try:
            d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
        except ValueError as e:
            raise ValidationError("from and to must be YYYY-MM-DD") from e
        if d1 < d0 or (d1 - d0).days > MAX_HISTORY_DAYS:
            raise ValidationError(f"date range must be 0-{MAX_HISTORY_DAYS} days")
        return self._bars.between(instrument.symbol, start, end)
