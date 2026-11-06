import os
from dataclasses import dataclass

from . import middleware
from .adapters.tickstream import TickstreamClient
from .adapters.transport import UrllibTransport
from .api.handlers import Handlers
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .limits import PlanLimiter, limit_key
from .observability import Logger, Metrics, stderr_logger
from .repositories.instruments import BarRepository, InstrumentRepository
from .router import Router
from .schema import SCHEMA
from .services.quotes import QuoteService


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    instruments: InstrumentRepository
    bars: BarRepository
    quotes: QuoteService
    logger: Logger
    metrics: Metrics


def build(db: Database, clock, ids, vendor_transport, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    instruments, bars = InstrumentRepository(db), BarRepository(db)
    vendor = TickstreamClient(vendor_transport, os.environ.get("TICKSTREAM_API_KEY", "ts_test"))
    quotes = QuoteService(instruments, bars, vendor, clock)
    router = Router()
    Handlers(quotes, metrics).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.errors(logger),
        middleware.access_log(logger, metrics, clock),
        middleware.rate_limit(PlanLimiter(clock), limit_key),
        middleware.authenticate(auth, public_paths={"/health"}),
    ])
    return Container(app, db, auth, instruments, bars, quotes, logger, metrics)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(), stderr_logger()).app
