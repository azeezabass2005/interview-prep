from dataclasses import dataclass

from . import middleware
from .api.handlers import Handlers
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .jobs import JOBS_SCHEMA, JobQueue, Worker
from .observability import Logger, Metrics, stderr_logger
from .ratelimit import FixedWindowLimiter
from .repositories.trades import AuditRepository, CounterpartyRepository, PositionRepository, TradeRepository
from .router import Router
from .schema import SCHEMA
from .services.eod import EndOfDay
from .services.trading import TradingService


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    counterparties: CounterpartyRepository
    positions: PositionRepository
    trading: TradingService
    eod: EndOfDay
    queue: JobQueue
    worker: Worker
    logger: Logger
    metrics: Metrics


def build(db: Database, clock, ids, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA, JOBS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    trades, positions = TradeRepository(db), PositionRepository(db)
    counterparties, audit = CounterpartyRepository(db), AuditRepository(db)
    trading = TradingService(db, trades, positions, counterparties, audit, clock, ids, logger)
    queue = JobQueue(db, clock, ids)
    eod = EndOfDay(positions, queue, clock, logger)
    worker = Worker(queue, {"eod_snapshot": eod.snapshot}, logger)
    router = Router()
    Handlers(trading, positions).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health"}),
        middleware.rate_limit(FixedWindowLimiter(clock, 600, 60), lambda r: r.principal.user_id),
    ])
    return Container(app, db, auth, counterparties, positions, trading, eod, queue, worker, logger, metrics)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), stderr_logger()).app
