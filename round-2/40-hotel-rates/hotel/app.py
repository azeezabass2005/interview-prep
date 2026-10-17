from .api import HotelApi
from .services.reservations import ReservationService
from .store import InMemoryStore


def build_app(clock):
    store = InMemoryStore()
    return HotelApi(ReservationService(store, clock)), store
