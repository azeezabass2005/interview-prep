import os
from dataclasses import dataclass

from . import middleware
from .adapters.paystream import PaystreamClient
from .adapters.transport import UrllibTransport
from .api.handlers import Handlers
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .observability import Logger, Metrics, stderr_logger
from .ratelimit import FixedWindowLimiter
from .repositories.payments import PaymentRepository, RefundRepository, WebhookEventRepository
from .router import Router
from .schema import SCHEMA
from .services.payments import PaymentService
from .services.webhooks import WebhookService

REQUESTS_PER_MINUTE = 300


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    payments: PaymentService
    webhooks: WebhookService
    logger: Logger
    metrics: Metrics


def build(db: Database, clock, ids, psp_transport, webhook_secret: str, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    payment_repo, refund_repo = PaymentRepository(db), RefundRepository(db)
    paystream = PaystreamClient(psp_transport, os.environ.get("PAYSTREAM_SECRET_KEY", "sk_test_paystream"))
    payments = PaymentService(payment_repo, refund_repo, paystream, clock, ids, logger, metrics)
    webhooks = WebhookService(webhook_secret, payment_repo, refund_repo, WebhookEventRepository(db), clock, logger)
    router = Router()
    Handlers(payments, webhooks).register(router)
    limiter = FixedWindowLimiter(clock, REQUESTS_PER_MINUTE, 60)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.authenticate(auth, public_paths={"/health", "/webhooks/paystream"}),
        middleware.rate_limit(limiter, lambda r: r.principal.org_id if r.principal else r.remote_addr),
    ])
    return Container(app, db, auth, payments, webhooks, logger, metrics)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(),
                 os.environ.get("PAYSTREAM_WEBHOOK_SECRET", "whsec_dev"), stderr_logger()).app
