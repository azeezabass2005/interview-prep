class CircuitBreaker:
    """Stops sending traffic to an upstream that keeps failing, so it can recover and our callers fail fast.

    closed: requests flow; `threshold` consecutive failures open the circuit.
    open: requests are refused immediately for `cooldown` seconds.
    half_open: after the cooldown, one trial request is let through; success closes the circuit, failure re-opens it.
    """

    def __init__(self, clock, threshold: int = 5, cooldown: float = 30.0):
        self._clock = clock
        self.threshold = threshold
        self.cooldown = cooldown
        self.state = "closed"
        self.failures = 0
        self.opened_at = 0.0

    def allow(self) -> bool:
        if self.state == "open":
            if self._clock.monotonic() - self.opened_at >= self.cooldown:
                self.state = "half_open"
                return True
            return False
        return True

    def record_success(self) -> None:
        if self.state == "half_open":
            self.state = "closed"

    def record_failure(self) -> None:
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.threshold:
            self.state = "open"
            self.opened_at = self._clock.monotonic()

    def snapshot(self) -> dict:
        return {"state": self.state, "failures": self.failures}
