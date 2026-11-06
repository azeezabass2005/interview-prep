import json

from .adapters.transport import TransportError, TransportTimeout
from .breaker import CircuitBreaker
from .errors import NotFound, ServiceUnavailable, UpstreamError
from .http import Request, Response
from .routes import Route, match

RETRYABLE_STATUS = {502, 503, 504}
MAX_ATTEMPTS = 3
# Request headers passed through to upstreams. Everything else (cookies, hop-by-hop headers, ...) is dropped.
FORWARDED_HEADERS = ("Authorization", "Content-Type", "Accept", "Idempotency-Key", "User-Agent")


class Proxy:
    def __init__(self, transport, clock, logger, metrics, partner_api_key: str):
        self._transport = transport
        self._clock = clock
        self._logger = logger
        self._metrics = metrics
        self._partner_api_key = partner_api_key
        self.breakers: dict[str, CircuitBreaker] = {}

    def breaker(self, route: Route) -> CircuitBreaker:
        return self.breakers.setdefault(route.name, CircuitBreaker(self._clock))

    def _upstream_headers(self, request: Request, route: Route) -> dict:
        headers = {name: request.headers.get(name) for name in FORWARDED_HEADERS if request.headers.get(name)}
        if route.external:
            headers["X-Api-Key"] = self._partner_api_key
        else:
            headers["X-Client-Id"] = request.principal.org_id
        return headers

    def forward(self, request: Request) -> Response:
        route = match(request.path)
        if route is None:
            raise NotFound(f"no route for {request.path}")
        breaker = self.breaker(route)
        if not breaker.allow():
            self._metrics.increment("upstream_rejected_total", upstream=route.name, reason="circuit_open")
            raise ServiceUnavailable(f"{route.name} is unavailable, retry later", retry_after=int(breaker.cooldown))
        url = route.base_url + request.path[len(route.prefix):]
        if request.query:
            url += "?" + "&".join(f"{k}={v}" for k, v in request.query.items())
        headers = self._upstream_headers(request, route)
        body = request.body or None
        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            started = self._clock.monotonic()
            try:
                result = self._transport.send(request.method, url, headers, body, route.timeout)
            except (TransportTimeout, TransportError) as e:
                last_error = f"{type(e).__name__}: {e}"
                self._metrics.increment("upstream_errors_total", upstream=route.name, kind="transport")
                continue
            finally:
                self._metrics.observe("upstream_duration_ms", (self._clock.monotonic() - started) * 1000, upstream=route.name)
            if result.status in RETRYABLE_STATUS:
                last_error = f"status {result.status}"
                self._metrics.increment("upstream_errors_total", upstream=route.name, kind=str(result.status))
                continue
            breaker.record_success()
            return Response(result.status, result.body)
        breaker.record_failure()
        self._logger.warning("upstream_failed", upstream=route.name, method=request.method, path=request.path,
                             attempts=MAX_ATTEMPTS, error=last_error, request_id=request.context.get("request_id"))
        raise UpstreamError(f"{route.name} failed: {last_error}")
