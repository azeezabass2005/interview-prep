from .api import LibraryApi
from .services.circulation import CirculationService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return LibraryApi(store, CirculationService(store)), store
