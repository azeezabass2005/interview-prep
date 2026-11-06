import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

from .clock import iso, parse_iso
from .errors import Forbidden, Unauthorized

TOKENS_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_tokens (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    org_id TEXT NOT NULL,
    roles TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT
);
"""


@dataclass(frozen=True)
class Principal:
    user_id: str
    org_id: str
    roles: frozenset

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def require_role(self, *roles: str) -> None:
        if not any(self.has_role(r) for r in roles):
            raise Forbidden(f"requires role: {' or '.join(roles)}")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class TokenAuthenticator:
    def __init__(self, db, clock):
        self._db = db
        self._clock = clock

    def issue(self, user_id: str, org_id: str, roles, ttl_hours: int = 12) -> str:
        token = "tok_" + secrets.token_urlsafe(24)
        expires = iso(self._clock.now() + timedelta(hours=ttl_hours))
        self._db.execute(
            "INSERT INTO api_tokens (token_hash, user_id, org_id, roles, expires_at) VALUES (?, ?, ?, ?, ?)",
            (hash_token(token), user_id, org_id, ",".join(sorted(roles)), expires),
        )
        return token

    def revoke(self, token: str) -> None:
        self._db.execute("UPDATE api_tokens SET revoked_at = ? WHERE token_hash = ?", (iso(self._clock.now()), hash_token(token)))

    def authenticate(self, token: str) -> Principal:
        row = self._db.query_one("SELECT * FROM api_tokens WHERE token_hash = ?", (hash_token(token),))
        if row is None or row["revoked_at"] is not None:
            raise Unauthorized("invalid token")
        if parse_iso(row["expires_at"]) <= self._clock.now():
            raise Unauthorized("token expired")
        return Principal(row["user_id"], row["org_id"], frozenset(r for r in row["roles"].split(",") if r))
