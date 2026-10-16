from .api import TourneyApi
from .services.play import PlayService
from .services.registration import RegistrationService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    reg = RegistrationService(store)
    return TourneyApi(reg, PlayService(reg)), store
