from .api import IndexApi
from .services.rebalance import RebalanceService
from .store import InMemoryStore


def build_app():
    return IndexApi(RebalanceService(InMemoryStore()))
