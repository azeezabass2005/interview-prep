import json
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from .errors import ValidationError


class Headers:
    """Case-insensitive HTTP headers that remember how each name was spelled."""

    def __init__(self, items=None):
        self._items: dict[str, tuple[str, str]] = {}
        for name, value in dict(items or {}).items():
            self[name] = value

    def __setitem__(self, name: str, value) -> None:
        self._items[name.lower()] = (name, str(value))

    def __getitem__(self, name: str) -> str:
        return self._items[name.lower()][1]

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._items

    def __delitem__(self, name: str) -> None:
        del self._items[name.lower()]

    def get(self, name: str, default=None):
        item = self._items.get(name.lower())
        return item[1] if item else default

    def items(self) -> list[tuple[str, str]]:
        return list(self._items.values())

    def copy(self) -> "Headers":
        return Headers(dict(self.items()))


@dataclass
class Request:
    method: str
    path: str
    headers: Headers = field(default_factory=Headers)
    query: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    remote_addr: str = "127.0.0.1"
    params: dict[str, str] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def build(cls, method: str, target: str, headers=None, body: bytes = b"", remote_addr: str = "127.0.0.1") -> "Request":
        parts = urlsplit(target)
        return cls(method.upper(), parts.path, Headers(headers or {}), dict(parse_qsl(parts.query)), body, remote_addr)

    def json(self) -> dict:
        if not self.body:
            return {}
        try:
            data = json.loads(self.body)
        except ValueError as e:
            raise ValidationError("request body is not valid JSON") from e
        if not isinstance(data, dict):
            raise ValidationError("request body must be a JSON object")
        return data

    @property
    def principal(self):
        return self.context.get("principal")


@dataclass
class Response:
    status: int = 200
    body: Any = None
    headers: Headers = field(default_factory=Headers)

    def encode(self) -> bytes:
        return b"" if self.body is None else json.dumps(self.body).encode()


def ok(body=None, status: int = 200) -> Response:
    return Response(status, body)
