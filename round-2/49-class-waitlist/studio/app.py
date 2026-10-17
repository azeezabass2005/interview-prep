from .api import StudioApi
from .services.booking import BookingService
from .services.members import MemberService
from .store import InMemoryStore


def build_app(clock):
    store = InMemoryStore()
    members = MemberService(store)
    return StudioApi(members, BookingService(store, members, clock))
