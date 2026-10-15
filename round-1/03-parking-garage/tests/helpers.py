from datetime import datetime

MON = datetime(2026, 3, 2)  # a Monday


def at(day_offset, hh, mm=0):
    return MON.replace(day=MON.day + day_offset, hour=hh, minute=mm)


class FakeClock:
    def __init__(self, now):
        self.current = now

    def now(self):
        return self.current
