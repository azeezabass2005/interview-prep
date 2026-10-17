from .api import LeagueApi
from .services.fixtures import FixtureService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return LeagueApi(store, FixtureService(store))
