from ..models import Org, User


class OrgRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, org: Org) -> None:
        self._db.execute("INSERT INTO orgs (id, name, kind) VALUES (?, ?, ?)", (org.id, org.name, org.kind))

    def get(self, org_id: str) -> Org | None:
        row = self._db.query_one("SELECT * FROM orgs WHERE id = ?", (org_id,))
        return Org(row["id"], row["name"], row["kind"]) if row else None


def _user(row) -> User:
    return User(row["id"], row["org_id"], row["email"], row["name"], bool(row["digest_enabled"]), row["last_digest_at"])


class UserRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, user: User) -> None:
        self._db.execute(
            "INSERT INTO users (id, org_id, email, name, digest_enabled, last_digest_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user.id, user.org_id, user.email.lower(), user.name, int(user.digest_enabled), user.last_digest_at),
        )

    def get(self, user_id: str) -> User | None:
        row = self._db.query_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return _user(row) if row else None

    def digest_recipients(self) -> list[User]:
        rows = self._db.query(
            "SELECT u.* FROM users u JOIN orgs o ON o.id = u.org_id WHERE u.digest_enabled = 1 AND o.kind = 'client' ORDER BY u.id"
        )
        return [_user(r) for r in rows]

    def set_last_digest(self, user_id: str, at: str) -> None:
        self._db.execute("UPDATE users SET last_digest_at = ? WHERE id = ?", (at, user_id))
