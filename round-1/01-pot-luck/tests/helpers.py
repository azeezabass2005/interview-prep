class FakeRng:
    """Deterministic stand-in for random.Random: returns queued values from randint."""

    def __init__(self, values):
        self._values = list(values)

    def randint(self, low, high):
        value = self._values.pop(0)
        assert low <= value <= high, f"{value} outside [{low}, {high}]"
        return value
