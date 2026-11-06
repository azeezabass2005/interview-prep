class AppError(Exception):
    status = 500
    code = "internal"

    def __init__(self, message: str = "", **extra):
        super().__init__(message)
        self.message = message or self.code.replace("_", " ")
        self.extra = extra


class ValidationError(AppError):
    status = 400
    code = "validation_error"


class Unauthorized(AppError):
    status = 401
    code = "unauthorized"


class Forbidden(AppError):
    status = 403
    code = "forbidden"


class NotFound(AppError):
    status = 404
    code = "not_found"


class MethodNotAllowed(AppError):
    status = 405
    code = "method_not_allowed"


class Conflict(AppError):
    status = 409
    code = "conflict"


class PayloadTooLarge(AppError):
    status = 413
    code = "payload_too_large"


class RateLimited(AppError):
    status = 429
    code = "rate_limited"


class UpstreamError(AppError):
    status = 502
    code = "upstream_error"


class ServiceUnavailable(AppError):
    status = 503
    code = "service_unavailable"
