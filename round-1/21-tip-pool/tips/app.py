from .api import TipsApi
from .services.tips import TipService
from .store import InMemoryStore


def build_app():
    return TipsApi(TipService(InMemoryStore()))
