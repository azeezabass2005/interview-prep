import os
from dataclasses import dataclass

from . import middleware
from .adapters.ratesy import RatesyClient
from .adapters.scanly import ScanlyClient
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
from .repositories.store import EmployeeRepository, ExpenseRepository, ReportRepository
from .router import Router
from .schema import SCHEMA
from .services.receipts import ReceiptScanner
from .services.reports import ReportService


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    employees: EmployeeRepository
    expenses: ExpenseRepository
    reports: ReportService
    scanner: ReceiptScanner
    queue: JobQueue
    worker: Worker
    logger: Logger


def build(db: Database, clock, ids, fx_transport, ocr_transport, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA, JOBS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    employees, report_repo, expenses = EmployeeRepository(db), ReportRepository(db), ExpenseRepository(db)
    fx = RatesyClient(fx_transport, os.environ.get("RATESY_API_KEY", "rt_test"))
    reports = ReportService(employees, report_repo, expenses, fx, clock, ids, logger)
    queue = JobQueue(db, clock, ids)
    scanner = ReceiptScanner(expenses, ScanlyClient(ocr_transport, os.environ.get("SCANLY_API_KEY", "sc_test")), queue, logger)
    worker = Worker(queue, {"ocr_batch": scanner.run}, logger)
    router = Router()
    Handlers(reports).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health"}),
        middleware.rate_limit(FixedWindowLimiter(clock, 300, 60), lambda r: r.principal.user_id),
    ])
    return Container(app, db, auth, employees, expenses, reports, scanner, queue, worker, logger)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(), UrllibTransport(), stderr_logger()).app
