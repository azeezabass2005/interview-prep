from .api import RideApi
from .services.surge import SurgeFeed
from .services.trips import TripService
from .store import InMemoryStore


def build_app(clock, surge: SurgeFeed = None):
    store = InMemoryStore()
    surge = surge or SurgeFeed()
    return RideApi(TripService(store, surge, clock)), surge, store
