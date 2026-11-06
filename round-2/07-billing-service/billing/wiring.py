import os
from dataclasses import dataclass

from . import middleware
from .adapters.taxly import TaxlyClient
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
from .repositories.ledger import ChargeRepository, CustomerRepository, InvoiceRepository, PaymentRepository, UsageRepository
from .router import Router
from .schema import SCHEMA
from .services.invoicing import InvoiceRun
from .services.payments import PaymentWebhooks
from .services.seats import SeatService


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    customers: CustomerRepository
    usage: UsageRepository
    invoices: InvoiceRepository
    payments: PaymentRepository
    seats: SeatService
    invoice_run: InvoiceRun
    queue: JobQueue
    worker: Worker
    logger: Logger


def build(db: Database, clock, ids, tax_transport, webhook_secret: str, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA, JOBS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    customers, usage, charges = CustomerRepository(db), UsageRepository(db), ChargeRepository(db)
    invoices, payments = InvoiceRepository(db), PaymentRepository(db)
    queue = JobQueue(db, clock, ids)
    tax = TaxlyClient(tax_transport, os.environ.get("TAXLY_API_KEY", "tx_test"))
    invoice_run = InvoiceRun(customers, usage, charges, invoices, tax, queue, clock, ids, logger)
    seats = SeatService(customers, charges, clock, ids)
    webhooks = PaymentWebhooks(webhook_secret, invoices, payments, clock, ids, logger)
    worker = Worker(queue, {"invoice_run": invoice_run.run}, logger)
    router = Router()
    Handlers(seats, usage, invoices, payments, webhooks, ids).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health", "/webhooks/paygate"}),
        middleware.rate_limit(FixedWindowLimiter(clock, 600, 60), lambda r: r.principal.org_id if r.principal else r.remote_addr),
    ])
    return Container(app, db, auth, customers, usage, invoices, payments, seats, invoice_run, queue, worker, logger)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(),
                 os.environ.get("PAYGATE_WEBHOOK_SECRET", "pg_dev"), stderr_logger()).app
