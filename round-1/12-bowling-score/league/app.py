from .api import LeagueApi
from .services.matches import MatchService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return LeagueApi(store, MatchService(store)), store
