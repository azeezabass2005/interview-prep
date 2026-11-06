from ..clock import iso


class EndOfDay:
    """Takes the end-of-day position snapshot that the overnight risk report reads. Scheduled at 21:30 New York time."""

    def __init__(self, positions, queue, clock, logger):
        self._positions = positions
        self._queue = queue
        self._clock = clock
        self._logger = logger

    def schedule(self) -> str:
        return self._queue.enqueue("eod_snapshot", {})

    def snapshot(self, payload: dict) -> None:
        now = self._clock.now()
        label = now.date().isoformat()
        rows = self._positions.snapshot(label, iso(now))
        self._logger.info("eod_snapshot", business_date=label, rows=rows)
