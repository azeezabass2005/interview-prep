class FakeClock:

    def __init__(self, t: float):
        self.t = t

    def time(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds
