import os
from dataclasses import dataclass

from . import middleware
from .adapters.transport import UrllibTransport
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .clock import SystemClock
from .db import Database
from .gateway import GatewayRouter
from .ids import IdGenerator
from .limits import SlidingWindowLimiter
from .observability import Logger, Metrics, stderr_logger
from .proxy import Proxy

REQUESTS_PER_MINUTE = 100


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    proxy: Proxy
    logger: Logger
    metrics: Metrics


def build(db: Database, clock, ids, transport, logger: Logger | None = None, partner_api_key: str = "fxp_test") -> Container:
    db.initialize(TOKENS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    proxy = Proxy(transport, clock, logger, metrics, partner_api_key)
    limiter = SlidingWindowLimiter(clock, REQUESTS_PER_MINUTE, 60)
    app = App(GatewayRouter(proxy), [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health"}),
        middleware.rate_limit(limiter, lambda r: r.principal.org_id),
    ])
    return Container(app, db, auth, proxy, logger, metrics)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(), stderr_logger(),
                 os.environ.get("FXPARTNER_API_KEY", "")).app
