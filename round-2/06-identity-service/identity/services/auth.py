import hashlib
import secrets
from datetime import timedelta

from ..auth import Principal
from ..clock import iso, parse_iso
from ..config import RESET_TOKEN_MINUTES, SESSION_ABSOLUTE_HOURS, SESSION_IDLE_MINUTES
from ..errors import NotFound, RateLimited, Unauthorized, ValidationError
from ..passwords import check_password, hash_password, validate_new_password


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self, users, sessions, resets, permissions, throttle, email, clock, logger, web_url: str):
        self._users = users
        self._sessions = sessions
        self._resets = resets
        self._permissions = permissions
        self._throttle = throttle
        self._email = email
        self._clock = clock
        self._logger = logger
        self._web_url = web_url

    def login(self, email: str, password: str) -> dict:
        key = email.strip()
        if self._throttle.locked(key):
            raise RateLimited("too many failed attempts; try again later", retry_after=15 * 60)
        user = self._users.by_email(email)
        if user is None:
            self._throttle.failed(key)
            raise NotFound("no account with that email")
        if user.disabled or not check_password(password, user.password_hash):
            self._throttle.failed(key)
            self._logger.warning("login_failed", user_id=user.id)
            raise Unauthorized("wrong password")
        self._throttle.succeeded(key)
        token = "ses_" + secrets.token_urlsafe(32)
        now = self._clock.now()
        expires = now + timedelta(minutes=SESSION_IDLE_MINUTES)
        self._sessions.add(_hash(token), user.id, iso(now), iso(expires))
        self._logger.info("login", user_id=user.id)
        return {"session_token": token, "expires_at": iso(expires), "user_id": user.id}

    def authenticate(self, token: str) -> Principal:
        """Validates a session and slides its idle expiry forward."""
        session = self._sessions.get(_hash(token))
        now = self._clock.now()
        if session is None or session["revoked_at"] is not None or parse_iso(session["expires_at"]) <= now:
            raise Unauthorized("session expired")
        user = self._users.get(session["user_id"])
        if user is None or user.disabled:
            raise Unauthorized("account disabled")
        self._sessions.extend(_hash(token), iso(now + timedelta(minutes=SESSION_IDLE_MINUTES)))
        return Principal(user.id, user.org_id, self._permissions.permissions(user.id))

    def logout(self, token: str) -> None:
        self._sessions.revoke(_hash(token), iso(self._clock.now()))

    def request_reset(self, email: str) -> None:
        """Always succeeds from the caller's point of view, so it can't be used to find out who has an account."""
        user = self._users.by_email(email)
        if user is None or user.disabled:
            return
        token = "rst_" + secrets.token_urlsafe(32)
        self._resets.add(_hash(token), user.id, iso(self._clock.now() + timedelta(minutes=RESET_TOKEN_MINUTES)))
        self._email.send(user.email, "Reset your password",
                         f"Reset your password within {RESET_TOKEN_MINUTES} minutes: {self._web_url}/reset?token={token}")

    def confirm_reset(self, token: str, new_password: str) -> None:
        row = self._resets.get(_hash(token))
        if row is None or row["used_at"] is not None or parse_iso(row["expires_at"]) <= self._clock.now():
            raise Unauthorized("this reset link is invalid or has expired")
        validate_new_password(new_password)
        self._users.set_password(row["user_id"], hash_password(new_password))
        self._sessions.revoke_all(row["user_id"], iso(self._clock.now()))
        self._logger.info("password_reset", user_id=row["user_id"])
