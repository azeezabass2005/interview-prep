from .errors import Forbidden
from .http import Request, Response


class GatewayRouter:
    """Our own endpoints by exact path; everything under a route prefix goes to the proxy."""

    def __init__(self, proxy):
        self._proxy = proxy
        self._own = {("GET", "/health"): self.health, ("GET", "/internal/upstreams"): self.upstreams}

    def resolve(self, method: str, path: str):
        handler = self._own.get((method, path))
        if handler is not None:
            return handler, {}, path
        return self._proxy.forward, {}, "proxy"

    def health(self, request: Request) -> Response:
        return Response(200, {"status": "ok"})

    def upstreams(self, request: Request) -> Response:
        if not request.principal.has_role("ops"):
            raise Forbidden("ops only")
        return Response(200, {name: b.snapshot() for name, b in self._proxy.breakers.items()})
