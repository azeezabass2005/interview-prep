from datetime import datetime

from .api import GarageApi
from .services.gates import GateService
from .services.occupancy import Occupancy
from .services.passes import PassService
from .store import InMemoryStore


class SystemClock:
    def now(self):
        return datetime.now()


def build_app(clock=None):
    store = InMemoryStore()
    passes = PassService(store)
    gates = GateService(store, passes, clock or SystemClock())
    return GarageApi(gates, passes, Occupancy(store)), store
