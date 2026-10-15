class FakeClock:
    def __init__(self, t: float = 1_780_000_000.0):
        self.t = t

    def time(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds
