from datetime import datetime

from fx.rates import RateBook


class FakeClock:
    def __init__(self):
        self.current = datetime(2026, 4, 1, 12, 0, 0)

    def now(self):
        return self.current


def standard_book():
    clock = FakeClock()
    book = RateBook(clock)
    book.set("EURUSD", "1.0850")
    book.set("GBPUSD", "1.2700")
    book.set("USDJPY", "151.20")
    book.set("USDCHF", "0.8800")
    return clock, book
