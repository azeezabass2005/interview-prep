import re

from .errors import MethodNotAllowed, NotFound


class Router:
    def __init__(self):
        self._routes = []

    def add(self, method: str, pattern: str, handler) -> None:
        regex = "^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", pattern) + "$"
        self._routes.append((method.upper(), re.compile(regex), handler, pattern))

    def get(self, pattern, handler):
        self.add("GET", pattern, handler)

    def post(self, pattern, handler):
        self.add("POST", pattern, handler)

    def patch(self, pattern, handler):
        self.add("PATCH", pattern, handler)

    def delete(self, pattern, handler):
        self.add("DELETE", pattern, handler)

    def resolve(self, method: str, path: str):
        allowed = []
        for route_method, regex, handler, pattern in self._routes:
            match = regex.match(path)
            if not match:
                continue
            if route_method == method:
                return handler, match.groupdict(), pattern
            allowed.append(route_method)
        if allowed:
            raise MethodNotAllowed(f"{method} not allowed on {path}")
        raise NotFound(f"no route for {path}")
