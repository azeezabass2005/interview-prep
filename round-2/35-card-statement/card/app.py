from .api import CardApi
from .services.cycle import CycleService
from .services.posting import PostingService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return CardApi(PostingService(store), CycleService(store))
