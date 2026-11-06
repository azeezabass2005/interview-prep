from ..models import User


def _user(row) -> User:
    return User(row["id"], row["org_id"], row["email"], row["name"], row["password_hash"], bool(row["disabled"]),
                row["created_at"])


class UserRepository:
    def __init__(self, db):
        self._db = db

    def add(self, u: User) -> None:
        self._db.execute("INSERT INTO users (id, org_id, email, name, password_hash, disabled, created_at) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (u.id, u.org_id, u.email.lower(), u.name, u.password_hash, int(u.disabled), u.created_at))

    def get(self, user_id: str) -> User | None:
        row = self._db.query_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return _user(row) if row else None

    def by_email(self, email: str) -> User | None:
        row = self._db.query_one("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        return _user(row) if row else None

    def in_org(self, org_id: str) -> list[User]:
        return [_user(r) for r in self._db.query("SELECT * FROM users WHERE org_id = ? ORDER BY email", (org_id,))]

    def set_password(self, user_id: str, password_hash: str) -> None:
        self._db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))

    def roles(self, user_id: str) -> set[str]:
        return {r["role"] for r in self._db.query("SELECT role FROM user_roles WHERE user_id = ?", (user_id,))}

    def grant(self, user_id: str, role: str) -> None:
        self._db.execute("INSERT OR IGNORE INTO user_roles (user_id, role) VALUES (?, ?)", (user_id, role))

    def revoke(self, user_id: str, role: str) -> None:
        self._db.execute("DELETE FROM user_roles WHERE user_id = ? AND role = ?", (user_id, role))


class SessionRepository:
    def __init__(self, db):
        self._db = db

    def add(self, token_hash: str, user_id: str, created_at: str, expires_at: str) -> None:
        self._db.execute("INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                         (token_hash, user_id, created_at, expires_at))

    def get(self, token_hash: str):
        return self._db.query_one("SELECT * FROM sessions WHERE token_hash = ?", (token_hash,))

    def extend(self, token_hash: str, expires_at: str) -> None:
        self._db.execute("UPDATE sessions SET expires_at = ? WHERE token_hash = ?", (expires_at, token_hash))

    def revoke(self, token_hash: str, at: str) -> None:
        self._db.execute("UPDATE sessions SET revoked_at = ? WHERE token_hash = ?", (at, token_hash))

    def revoke_all(self, user_id: str, at: str) -> None:
        self._db.execute("UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL", (at, user_id))


class ResetTokenRepository:
    def __init__(self, db):
        self._db = db

    def add(self, token_hash: str, user_id: str, expires_at: str) -> None:
        self._db.execute("INSERT INTO reset_tokens (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                         (token_hash, user_id, expires_at))

    def get(self, token_hash: str):
        return self._db.query_one("SELECT * FROM reset_tokens WHERE token_hash = ?", (token_hash,))

    def mark_used(self, token_hash: str, at: str) -> bool:
        return self._db.execute("UPDATE reset_tokens SET used_at = ? WHERE token_hash = ? AND used_at IS NULL",
                                (at, token_hash)) == 1
