from .api import DripApi
from .register import ShareRegister
from .services.enrolment import EnrolmentService
from .services.processor import DividendProcessor
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    register = ShareRegister()
    enrolment = EnrolmentService(store)
    return DripApi(store, register, enrolment, DividendProcessor(store, register, enrolment)), store
