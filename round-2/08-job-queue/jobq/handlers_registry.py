from typing import Callable, Dict

Handler = Callable[[dict, "object"], None]


class HandlerRegistry:
    def __init__(self):
        self._handlers: Dict[str, Handler] = {}

    def register(self, kind: str, fn: Handler) -> None:
        self._handlers[kind] = fn

    def get(self, kind: str) -> Handler:
        if kind not in self._handlers:
            raise KeyError(f"no handler for job kind {kind!r}")
        return self._handlers[kind]
