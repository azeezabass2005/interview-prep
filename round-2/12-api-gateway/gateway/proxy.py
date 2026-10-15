from dataclasses import dataclass, field

from .auth import Authenticator
from .limiter import RateLimiter


@dataclass
class Request:
    path: str
    api_key: str = None


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)


class Gateway:
    def __init__(self, auth: Authenticator, limiter: RateLimiter, upstream):
        self._auth = auth
        self._limiter = limiter
        self._upstream = upstream

    def handle(self, request: Request) -> Response:
        identity = self._auth.identify(request.api_key)
        if identity is None:
            return Response(401, {"error": "invalid API key"})
        tenant_id, user_id = identity
        decision = self._limiter.check(tenant_id, user_id)
        headers = {"X-RateLimit-Limit": str(decision.limit), "X-RateLimit-Remaining": str(decision.remaining)}
        if not decision.allowed:
            headers["Retry-After"] = str(decision.retry_after)
            return Response(429, {"error": "rate limit exceeded"}, headers)
        return Response(200, self._upstream.forward(request.path), headers)
