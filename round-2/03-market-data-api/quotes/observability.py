import json
import sys

SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}


def redact_headers(headers) -> dict:
    return {name: ("[REDACTED]" if name.lower() in SENSITIVE_HEADERS else value) for name, value in headers.items()}


class Logger:
    """Structured JSON logs. Records are kept in memory as well, for tests and the admin log viewer."""

    def __init__(self, stream=None):
        self.records: list[dict] = []
        self._stream = stream

    def _log(self, level: str, event: str, fields: dict) -> None:
        record = {"level": level, "event": event, **fields}
        self.records.append(record)
        if self._stream is not None:
            self._stream.write(json.dumps(record, default=str) + "\n")

    def info(self, event: str, **fields) -> None:
        self._log("info", event, fields)

    def warning(self, event: str, **fields) -> None:
        self._log("warning", event, fields)

    def error(self, event: str, **fields) -> None:
        self._log("error", event, fields)

    def events(self, event: str) -> list[dict]:
        return [r for r in self.records if r["event"] == event]


def stderr_logger() -> Logger:
    return Logger(sys.stderr)


class Metrics:
    def __init__(self):
        self.counters: dict[tuple, float] = {}
        self.timings: dict[tuple, list[float]] = {}

    @staticmethod
    def _key(name: str, labels: dict) -> tuple:
        return (name, tuple(sorted((k, str(v)) for k, v in labels.items())))

    def increment(self, name: str, value: float = 1, **labels) -> None:
        key = self._key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value

    def observe(self, name: str, value: float, **labels) -> None:
        self.timings.setdefault(self._key(name, labels), []).append(value)

    def count(self, name: str, **labels) -> float:
        """Sum of a counter over every series matching the given labels."""
        want = {(k, str(v)) for k, v in labels.items()}
        return sum(v for (n, lbls), v in self.counters.items() if n == name and want <= set(lbls))
