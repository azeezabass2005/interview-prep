import secrets
from datetime import timedelta

from ..audit import Audit
from ..config import MIN_PASSWORD_LENGTH, RESET_TOKEN_TTL_MINUTES
from ..db import Database
from ..errors import AccountsError, InvalidToken
from ..repositories.tokens import TokenRepository
from ..repositories.users import UserRepository
from .passwords import hash_password


class PasswordResetService:
    def __init__(self, db: Database, clock):
        self._users = UserRepository(db)
        self._tokens = TokenRepository(db)
        self._audit = Audit(db, clock)
        self._clock = clock

    def request_reset(self, email: str):
        user = self._users.by_email(email)
        if user is None or user.deleted_at is not None:
            return None
        token = secrets.token_urlsafe(24)
        self._tokens.create(token, user.user_id, self._clock.now())
        return token

    def reset(self, token: str, new_password: str) -> None:
        if len(new_password or "") < MIN_PASSWORD_LENGTH:
            raise AccountsError("password too short")
        record = self._tokens.get(token)
        if record is None or record.used_at is not None:
            raise InvalidToken("invalid or used token")
        if self._clock.now() - record.created_at > timedelta(minutes=RESET_TOKEN_TTL_MINUTES):
            raise InvalidToken("token expired")
        password_hash, salt = hash_password(new_password)
        self._users.set_password(record.user_id, password_hash, salt)
        self._audit.log(record.user_id, "password_reset")
