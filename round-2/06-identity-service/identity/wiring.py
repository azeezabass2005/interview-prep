import os
from dataclasses import dataclass

from . import middleware
from .adapters.postbox import PostboxClient
from .adapters.transport import UrllibTransport
from .api.handlers import Handlers
from .app import App
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .observability import Logger, Metrics, stderr_logger
from .ratelimit import FixedWindowLimiter
from .repositories.accounts import ResetTokenRepository, SessionRepository, UserRepository
from .router import Router
from .schema import SCHEMA
from .services.auth import AuthService
from .services.permissions import PermissionService
from .services.throttle import LoginThrottle

PUBLIC = {"/health", "/login", "/password-reset", "/password-reset/confirm"}


@dataclass
class Container:
    app: App
    db: Database
    users: UserRepository
    auth: AuthService
    permissions: PermissionService
    logger: Logger


def build(db: Database, clock, ids, email_transport, logger: Logger | None = None,
          web_url: str = "https://accounts.markets.example") -> Container:
    db.initialize(SCHEMA)
    logger = logger or Logger()
    metrics = Metrics()
    users = UserRepository(db)
    permissions = PermissionService(users, clock)
    email = PostboxClient(email_transport, os.environ.get("POSTBOX_API_KEY", "pb_test"))
    auth = AuthService(users, SessionRepository(db), ResetTokenRepository(db), permissions, LoginThrottle(clock), email, clock,
                       logger, web_url)
    router = Router()
    Handlers(auth, users, permissions, clock, ids).register(router)
    app = App(router, [
        middleware.request_id(ids),
        middleware.access_log(logger, metrics, clock),
        middleware.errors(logger),
        middleware.rate_limit(FixedWindowLimiter(clock, 300, 60), lambda r: r.remote_addr),
        middleware.authenticate(auth, public_paths=PUBLIC),
    ])
    return Container(app, db, users, auth, permissions, logger)


def build_production_app(db_path: str) -> App:
    return build(Database(db_path), SystemClock(), IdGenerator(), UrllibTransport(), stderr_logger(),
                 os.environ.get("WEB_URL", "http://localhost:3000")).app
