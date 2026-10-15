from datetime import datetime, timedelta

from classes.booking import BookingService
from classes.models import FitnessClass, Member

START = datetime(2026, 9, 1, 18, 0)


class FakeClock:
    def __init__(self):
        self.current = START - timedelta(days=2)

    def now(self):
        return self.current

    def hours_before_start(self, hours):
        self.current = START - timedelta(hours=hours)


def setup(capacity=1):
    clock = FakeClock()
    return clock, BookingService(clock), FitnessClass("spin-1", START, capacity)


ANA, SAM, PIA, BEA = Member("ana"), Member("sam"), Member("pia", premium=True), Member("bea")
