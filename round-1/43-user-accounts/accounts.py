import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

MIN_LENGTH = 12
MAX_FAILURES = 5
LOCK_FOR = timedelta(minutes=15)
TOKEN_TTL = timedelta(minutes=30)
ITERATIONS = 1000


class AccountError(Exception):
    pass


@dataclass
class User:
    email: str
    salt: bytes
    password_hash: bytes
    failures: int = 0
    locked_until: Optional[datetime] = None
    tokens: Dict[str, datetime] = field(default_factory=dict)


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)


class Accounts:
    def __init__(self, clock):
        self.clock = clock
        self.users = {}

    @staticmethod
    def _key(email):
        return email.strip()

    def _check_password(self, email, password):
        if len(password) < MIN_LENGTH:
            raise AccountError("password too short")
        if not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
            raise AccountError("password needs a letter and a digit")

    def sign_up(self, email, password):
        key = self._key(email)
        if key in self.users:
            raise AccountError("email already registered")
        self._check_password(key, password)
        salt = os.urandom(16)
        self.users[key] = User(key, salt, _hash(password, salt))
        return self.users[key]

    def _user(self, email):
        user = self.users.get(self._key(email))
        if user is None:
            raise AccountError("unknown user")
        return user

    def login(self, email, password):
        user = self._user(email)
        now = self.clock.now()
        if user.locked_until and now < user.locked_until:
            return False
        if hmac.compare_digest(_hash(password, user.salt), user.password_hash):
            return True
        user.failures += 1
        if user.failures >= MAX_FAILURES:
            user.locked_until = now + LOCK_FOR
            user.failures = 0
        return False

    def request_reset(self, email):
        user = self._user(email)
        token = secrets.token_urlsafe(16)
        user.tokens = {token: self.clock.now() + TOKEN_TTL}
        return token

    def reset(self, email, token, new_password):
        user = self._user(email)
        expires = user.tokens.get(token)
        if expires is None or self.clock.now() >= expires:
            raise AccountError("invalid or expired token")
        self._check_password(user.email, new_password)
        user.salt = os.urandom(16)
        user.password_hash = _hash(new_password, user.salt)
