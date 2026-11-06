import os
from dataclasses import dataclass

from . import middleware
from .adapters.postbox import PostboxClient
from .adapters.transport import UrllibTransport
from .api.handlers import ReportHandlers
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .cache import TTLCache
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .jobs import JOBS_SCHEMA, JobQueue, Worker
from .observability import Logger, Metrics, stderr_logger
from .ratelimit import FixedWindowLimiter
from .repositories.entitlements import EntitlementRepository
from .repositories.orgs import OrgRepository, UserRepository
from .repositories.reports import ReportRepository
from .router import Router
from .schema import SCHEMA
from .services.digest import DigestService
from .services.reports import ReportService

LIST_CACHE_SECONDS = 60
REQUESTS_PER_MINUTE = 120


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    orgs: OrgRepository
    users: UserRepository
    entitlements: EntitlementRepository
    reports: ReportService
    digest: DigestService
    queue: JobQueue
    worker: Worker
    cache: TTLCache
    logger: Logger
    metrics: Metrics


def build(db: Database, clock, ids, email_transport, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA, JOBS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    orgs, users = OrgRepository(db), UserRepository(db)
    entitlements, report_repo = EntitlementRepository(db), ReportRepository(db)
    cache = TTLCache(clock, LIST_CACHE_SECONDS)
    queue = JobQueue(db, clock, ids)
    reports = ReportService(report_repo, entitlements, orgs, cache, clock, ids)
    email = PostboxClient(email_transport, os.environ.get("POSTBOX_API_KEY", "pbx_test_key"))
    digest = DigestService(users, report_repo, entitlements, email, queue, clock, logger)
    worker = Worker(queue, {"send_digest": digest.send_digest}, logger)

    router = Router()
    ReportHandlers(reports).register(router)
    limiter = FixedWindowLimiter(clock, REQUESTS_PER_MINUTE, 60)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health"}),
        middleware.rate_limit(limiter, lambda r: r.principal.user_id if r.principal else r.remote_addr),
    ])
    return Container(app, db, auth, orgs, users, entitlements, reports, digest, queue, worker, cache, logger, metrics)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(), stderr_logger()).app
