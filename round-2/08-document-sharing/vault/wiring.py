from dataclasses import dataclass

from . import middleware
from .api.handlers import Handlers
from .app import App
from .auth import TOKENS_SCHEMA, TokenAuthenticator
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .limits import body_limit
from .observability import Logger, Metrics, stderr_logger
from .ratelimit import FixedWindowLimiter
from .repositories.documents import DocumentRepository, LinkRepository
from .router import Router
from .schema import SCHEMA
from .services.documents import DocumentService


class PublicLinks:
    """Share links (/s/<token>) are opened without logging in."""

    def __contains__(self, path: str) -> bool:
        return path == "/health" or path.startswith("/s/")


@dataclass
class Container:
    app: App
    db: Database
    auth: TokenAuthenticator
    docs: DocumentService
    logger: Logger


def build(db: Database, clock, ids, logger: Logger | None = None) -> Container:
    db.initialize(SCHEMA, TOKENS_SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    auth = TokenAuthenticator(db, clock)
    docs = DocumentService(DocumentRepository(db), LinkRepository(db), clock, ids, logger)
    router = Router()
    Handlers(docs).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        body_limit(),
        middleware.authenticate(auth, public_paths=PublicLinks()),
        middleware.rate_limit(FixedWindowLimiter(clock, 600, 60), lambda r: r.principal.user_id if r.principal else r.remote_addr),
    ])
    return Container(app, db, auth, docs, logger)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), stderr_logger()).app
