import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field


class TransportTimeout(Exception):
    pass


class TransportError(Exception):
    pass


@dataclass
class HttpResult:
    status: int
    body: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)


class UrllibTransport:
    """Real HTTP for production. Tests use FakeTransport instead."""

    def send(self, method: str, url: str, headers: dict, body: bytes | None, timeout: float) -> HttpResult:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return HttpResult(resp.status, json.loads(resp.read() or b"{}"), dict(resp.headers))
        except urllib.error.HTTPError as e:
            return HttpResult(e.code, json.loads(e.read() or b"{}"), dict(e.headers))
        except TimeoutError as e:
            raise TransportTimeout(str(e)) from e
        except urllib.error.URLError as e:
            raise TransportError(str(e)) from e


@dataclass
class Call:
    method: str
    url: str
    headers: dict
    body: bytes | None
    timeout: float

    def json(self) -> dict:
        return json.loads(self.body) if self.body else {}


class FakeTransport:
    """Scripted responses for tests. Queue results (HttpResult) or exceptions; every call is recorded."""

    def __init__(self, default: HttpResult | None = None):
        self.calls: list[Call] = []
        self._script: list = []
        self._default = default or HttpResult(200, {})

    def queue(self, *results) -> "FakeTransport":
        self._script.extend(results)
        return self

    def send(self, method: str, url: str, headers: dict, body: bytes | None, timeout: float) -> HttpResult:
        self.calls.append(Call(method, url, dict(headers), body, timeout))
        result = self._script.pop(0) if self._script else self._default
        if isinstance(result, Exception):
            raise result
        return result
