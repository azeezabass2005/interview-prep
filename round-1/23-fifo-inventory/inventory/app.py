from .api import InventoryApi
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return InventoryApi(store), store
