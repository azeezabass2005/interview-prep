from .http import Request, Response
from .router import Router


class App:
    """Runs a request through the middleware stack (outermost first), then the matched route."""

    def __init__(self, router: Router, middleware: list):
        self.router = router
        self.middleware = middleware

    def _endpoint(self, request: Request) -> Response:
        handler, params, pattern = self.router.resolve(request.method, request.path)
        request.params = params
        request.context["route"] = pattern
        return handler(request)

    def handle(self, request: Request) -> Response:
        call = self._endpoint
        for mw in reversed(self.middleware):
            call = _wrap(mw, call)
        return call(request)


def _wrap(mw, call_next):
    return lambda request: mw(request, call_next)
