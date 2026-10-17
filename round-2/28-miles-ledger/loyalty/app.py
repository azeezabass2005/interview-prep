from .api import LoyaltyApi
from .services.flights import FlightService
from .services.ledger import Ledger
from .services.status import StatusService
from .services.transfers import TransferService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    status = StatusService(store)
    ledger = Ledger(store, status)
    return LoyaltyApi(store, status, ledger, FlightService(store, status), TransferService(store, ledger)), store
