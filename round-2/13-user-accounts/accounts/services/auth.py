from datetime import timedelta

from ..audit import Audit
from ..config import LOCKOUT_MINUTES, MAX_FAILED_LOGINS
from ..db import Database
from ..errors import AccountLocked, InvalidCredentials
from ..models import User
from ..repositories.users import UserRepository
from .passwords import verify_password


class AuthService:
    def __init__(self, db: Database, clock):
        self._users = UserRepository(db)
        self._audit = Audit(db, clock)
        self._clock = clock

    def login(self, email: str, password: str) -> User:
        user = self._users.by_email(email)
        if user is None or user.deleted_at is not None:
            raise InvalidCredentials("invalid e-mail or password")
        now = self._clock.now()

        if not verify_password(password, user.password_hash, user.salt):
            if user.locked_until is not None and user.locked_until > now:
                self._audit.log(user.user_id, "login_locked")
                raise AccountLocked("account temporarily locked")
            failed = user.failed_attempts + 1
            locked_until = now + timedelta(minutes=LOCKOUT_MINUTES) if failed >= MAX_FAILED_LOGINS else user.locked_until
            self._users.record_login_result(user.user_id, failed, locked_until)
            self._audit.log(user.user_id, "login_failed")
            raise InvalidCredentials("invalid e-mail or password")

        self._users.record_login_result(user.user_id, 0, None)
        self._audit.log(user.user_id, "login_ok")
        return user
