from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    prefix: str          # public path prefix
    name: str            # upstream name, used for metrics and the circuit breaker
    base_url: str        # where requests are sent; the path after the prefix is appended
    external: bool       # a third party outside our network
    timeout: float


ROUTES = [
    Route("/v1/orders", "orders", "http://orders.internal:8080/orders", external=False, timeout=5.0),
    Route("/v1/quotes", "quotes", "http://quotes.internal:8080/quotes", external=False, timeout=2.0),
    Route("/v1/accounts", "accounts", "http://accounts.internal:8080/accounts", external=False, timeout=3.0),
    Route("/v1/fx", "fxpartner", "https://api.fxpartner.example/v2/rates", external=True, timeout=4.0),
]


def match(path: str) -> Route | None:
    for route in ROUTES:
        if path == route.prefix or path.startswith(route.prefix + "/"):
            return route
    return None
