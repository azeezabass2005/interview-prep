from .api import MarginApi
from .services.calls import CallService
from .services.prices import PriceService
from .services.valuation import Valuation
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    prices = PriceService(store)
    valuation = Valuation(store, prices)
    return MarginApi(store, prices, valuation, CallService(store, valuation))
