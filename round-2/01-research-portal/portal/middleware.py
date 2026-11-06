import traceback

from .errors import AppError, RateLimited, Unauthorized
from .http import Request, Response
from .observability import redact_headers


def request_id(ids):
    def middleware(request: Request, call_next) -> Response:
        rid = request.headers.get("X-Request-ID") or ids.new("req")
        request.context["request_id"] = rid
        response = call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
    return middleware


def error_response(error: AppError, request: Request) -> Response:
    body = {"error": {"code": error.code, "message": error.message, "request_id": request.context.get("request_id")}}
    response = Response(error.status, body)
    if isinstance(error, RateLimited):
        response.headers["Retry-After"] = error.extra.get("retry_after", 1)
    return response


def errors(logger):
    def middleware(request: Request, call_next) -> Response:
        try:
            return call_next(request)
        except AppError as e:
            return error_response(e, request)
        except Exception:
            logger.error("unhandled_error", request_id=request.context.get("request_id"), path=request.path,
                         trace=traceback.format_exc())
            body = {"error": {"code": "internal", "message": "Internal server error",
                              "request_id": request.context.get("request_id")}}
            return Response(500, body)
    return middleware


def access_log(logger, metrics, clock):
    def middleware(request: Request, call_next) -> Response:
        started = clock.monotonic()
        response = call_next(request)
        elapsed_ms = round((clock.monotonic() - started) * 1000, 1)
        route = request.context.get("route", "unmatched")
        logger.info("request", method=request.method, path=request.path, query=dict(request.query),
                    status=response.status, duration_ms=elapsed_ms,
                    request_id=request.context.get("request_id"), headers=redact_headers(request.headers))
        metrics.increment("http_requests_total", method=request.method, route=route, status=response.status)
        metrics.observe("http_request_duration_ms", elapsed_ms, route=route)
        return response
    return middleware


def authenticate(authenticator, public_paths=()):
    def middleware(request: Request, call_next) -> Response:
        if request.path in public_paths:
            return call_next(request)
        header = request.headers.get("Authorization", "")
        if not header and request.path.endswith("/pdf") and "access_token" in request.query:
            header = "Bearer " + request.query["access_token"]
        if not header.startswith("Bearer "):
            raise Unauthorized("missing bearer token")
        request.context["principal"] = authenticator.authenticate(header[len("Bearer "):].strip())
        return call_next(request)
    return middleware


def rate_limit(limiter, key_for):
    def middleware(request: Request, call_next) -> Response:
        decision = limiter.check(key_for(request))
        if not decision.allowed:
            raise RateLimited("too many requests", retry_after=decision.retry_after)
        response = call_next(request)
        response.headers["X-RateLimit-Remaining"] = decision.remaining
        return response
    return middleware
