import uuid


class IdGenerator:
    def new(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"


class SequentialIds(IdGenerator):
    """Predictable ids for tests and fixtures."""

    def __init__(self):
        self._n = 0

    def new(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}_{self._n:04d}"
