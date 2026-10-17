from .api import FxApi
from .services.payments import PaymentService
from .services.quotes import QuoteService
from .services.rates import RateBook
from .store import InMemoryStore


def build_app(clock):
    store = InMemoryStore()
    rates = RateBook(store, clock)
    return FxApi(rates, QuoteService(store, rates, clock), PaymentService(store, clock))
