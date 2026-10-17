from .api import MeteringApi
from .services.limiter import Limiter
from .store import InMemoryStore


def build_app(clock):
    store = InMemoryStore()
    return MeteringApi(store, Limiter(store, clock)), store
