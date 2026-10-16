from .api import UtilityApi
from .services.billing import BillingService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    return UtilityApi(store, BillingService(store))
