from .api import BondApi
from .calendar import BusinessCalendar
from .services.booking import BookingService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    calendar = BusinessCalendar()
    return BondApi(BookingService(store, calendar), calendar), store
