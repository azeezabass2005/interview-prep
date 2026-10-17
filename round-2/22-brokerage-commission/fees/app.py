from .api import FeeApi
from .services.statements import StatementService
from .services.trades import TradeService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return FeeApi(TradeService(store), StatementService(store)), store
