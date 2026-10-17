from datetime import datetime

from .api import PotLuckApi
from .codes import CodeGenerator
from .services.draws import DrawService
from .services.entries import EntryService
from .services.participants import ParticipantService
from .store import InMemoryStore


class SystemClock:
    def now(self):
        return datetime.now()


def build_app(rng=None, clock=None):
    store = InMemoryStore()
    clock = clock or SystemClock()
    codes = CodeGenerator(rng)
    participants = ParticipantService(store)
    draws = DrawService(store, codes, clock)
    entries = EntryService(store, draws, participants, codes, clock)
    return PotLuckApi(store, participants, draws, entries), store
