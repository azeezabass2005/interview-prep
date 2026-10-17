import itertools
from datetime import timedelta
from decimal import ROUND_DOWN, Decimal

MINOR_UNITS = {"USD": 2, "EUR": 2, "GBP": 2, "JPY": 0}
SPREAD = Decimal("0.005")
QUOTE_TTL = timedelta(seconds=30)
DAILY_LIMIT_USD = Decimal("50000")


class FxError(Exception):
    pass


class FxDesk:
    def __init__(self, clock):
        self.clock = clock
        self.rates = {"USD": Decimal(1)}
        self.quotes = {}
        self.bookings = []
        self._ids = itertools.count(1)

    def set_rate(self, currency, per_usd):
        if currency not in MINOR_UNITS or currency == "USD":
            raise FxError("unsupported currency")
        self.rates[currency] = Decimal(str(per_usd))

    def mid(self, source, target):
        for c in (source, target):
            if c not in self.rates:
                raise FxError(f"no rate for {c}")
        if source == target:
            return Decimal(1)
        if source == "USD":
            return self.rates[target]
        if target == "USD":
            return 1 / self.rates[source]
        return self.rates[source] / self.rates[target]

    def quote(self, client, source, target, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise FxError("amount must be positive")
        rate = self.mid(source, target) * (1 + SPREAD)
        receive = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        quote = {"quote_id": next(self._ids), "client": client, "source": source, "target": target, "amount": amount,
                 "rate": rate, "receive": receive, "usd_mid": self.mid(source, "USD"),
                 "expires_at": self.clock.now() + QUOTE_TTL, "status": "QUOTED"}
        self.quotes[quote["quote_id"]] = quote
        return quote

    def book(self, quote_id):
        quote = self.quotes.get(quote_id)
        if quote is None or quote["status"] != "QUOTED":
            raise FxError("quote not available")
        now = self.clock.now()
        if now >= quote["expires_at"]:
            raise FxError("quote expired")
        usd = quote["amount"]
        used = sum(b["usd"] for b in self.bookings if b["client"] == quote["client"] and b["day"] == now.date())
        if used + usd > DAILY_LIMIT_USD:
            raise FxError("daily limit exceeded")
        quote["status"] = "BOOKED"
        self.bookings.append({"quote_id": quote_id, "client": quote["client"], "day": now.date(), "usd": usd})
        return quote

    def cancel(self, quote_id):
        quote = self.quotes.get(quote_id)
        if quote is None or quote["status"] != "QUOTED":
            raise FxError("only open quotes can be cancelled")
        quote["status"] = "CANCELLED"
        return quote

    def expire_quotes(self):
        now = self.clock.now()
        expired = [q for q in self.quotes.values() if q["status"] == "QUOTED" and now > q["expires_at"]]
        for q in expired:
            q["status"] = "EXPIRED"
        return len(expired)

    def usage(self, client, day):
        used = sum((b["usd"] for b in self.bookings if b["client"] == client and b["day"] == day), Decimal("0"))
        return {"used_usd": used, "remaining_usd": max(DAILY_LIMIT_USD - used, Decimal("0"))}

    def blotter(self, day):
        rows = []
        for b in self.bookings:
            if b["day"] == day:
                q = self.quotes[b["quote_id"]]
                rows.append((q["client"], q["source"], q["amount"], q["target"], q["receive"]))
        return sorted(rows)
