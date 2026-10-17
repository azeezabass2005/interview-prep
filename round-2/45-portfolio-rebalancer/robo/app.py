from .api import RoboApi
from .services.accounts import AccountService
from .services.prices import PriceService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return RoboApi(store, AccountService(store), PriceService(store))
