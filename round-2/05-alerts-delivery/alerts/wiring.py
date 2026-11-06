import os
from dataclasses import dataclass

from . import middleware
from .adapters.channels import PostboxClient, TextwireClient
from .adapters.transport import UrllibTransport
from .api.handlers import Handlers
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .jobs import JOBS_SCHEMA, JobQueue, Worker
from .observability import Logger, Metrics, stderr_logger
from .ratelimit import FixedWindowLimiter
from .repositories.store import DeliveryRepository, RuleRepository, UserRepository
from .router import Router
from .schema import SCHEMA
from .services.delivery import AlertEngine
from .services.rules import RuleService


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    users: UserRepository
    deliveries: DeliveryRepository
    engine: AlertEngine
    queue: JobQueue
    logger: Logger
    metrics: Metrics

    def worker(self) -> Worker:
        """A worker process. Production runs two of them against the same queue."""
        return Worker(self.queue, {"deliver": self.engine.deliver}, self.logger)


def build(db: Database, clock, ids, sms_transport, email_transport, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA, JOBS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    users, rules, deliveries = UserRepository(db), RuleRepository(db), DeliveryRepository(db)
    queue = JobQueue(db, clock, ids)
    sms = TextwireClient(sms_transport, os.environ.get("TEXTWIRE_API_KEY", "tw_test"))
    email = PostboxClient(email_transport, os.environ.get("POSTBOX_API_KEY", "pb_test"))
    engine = AlertEngine(rules, users, deliveries, queue, sms, email, clock, ids, logger, metrics)
    router = Router()
    Handlers(RuleService(rules, users, clock, ids), engine, deliveries).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health"}),
        middleware.rate_limit(FixedWindowLimiter(clock, 1_000, 60), lambda r: r.principal.user_id),
    ])
    return Container(app, db, auth, users, deliveries, engine, queue, logger, metrics)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(), UrllibTransport(), stderr_logger()).app
