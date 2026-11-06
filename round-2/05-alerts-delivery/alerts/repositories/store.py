from ..models import Delivery, Rule, User

RULE_COLUMNS = "id, user_id, symbol, direction, threshold, channel, active, created_at, triggered_at"
DELIVERY_COLUMNS = "id, rule_id, user_id, channel, recipient, message, status, provider_id, error, created_at, sent_at"


def _rule(row) -> Rule:
    r = Rule(*(row[c] for c in RULE_COLUMNS.split(", ")))
    r.active = bool(r.active)
    return r


def _delivery(row) -> Delivery:
    return Delivery(*(row[c] for c in DELIVERY_COLUMNS.split(", ")))


class UserRepository:
    def __init__(self, db):
        self._db = db

    def add(self, u: User) -> None:
        self._db.execute("INSERT INTO users (id, org_id, name, email, phone) VALUES (?, ?, ?, ?, ?)",
                         (u.id, u.org_id, u.name, u.email, u.phone))

    def get(self, user_id: str) -> User | None:
        row = self._db.query_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return User(row["id"], row["org_id"], row["name"], row["email"], row["phone"]) if row else None


class RuleRepository:
    def __init__(self, db):
        self._db = db

    def add(self, r: Rule) -> None:
        self._db.execute(f"INSERT INTO rules ({RULE_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (r.id, r.user_id, r.symbol, r.direction, r.threshold, r.channel, int(r.active), r.created_at,
                          r.triggered_at))

    def get(self, rule_id: str) -> Rule | None:
        row = self._db.query_one(f"SELECT {RULE_COLUMNS} FROM rules WHERE id = ?", (rule_id,))
        return _rule(row) if row else None

    def for_user(self, user_id: str) -> list[Rule]:
        return [_rule(r) for r in self._db.query(f"SELECT {RULE_COLUMNS} FROM rules WHERE user_id = ? ORDER BY created_at, id",
                                                 (user_id,))]

    def active_for_symbol(self, symbol: str) -> list[Rule]:
        return [_rule(r) for r in self._db.query(f"SELECT {RULE_COLUMNS} FROM rules WHERE symbol = ? AND active = 1 ORDER BY id",
                                                 (symbol,))]

    def mark_triggered(self, rule_id: str, at: str) -> bool:
        """One-shot: only the first price that crosses the threshold triggers the rule."""
        return self._db.execute("UPDATE rules SET active = 0, triggered_at = ? WHERE id = ? AND active = 1", (at, rule_id)) == 1

    def delete(self, rule_id: str) -> None:
        self._db.execute("DELETE FROM rules WHERE id = ?", (rule_id,))


class DeliveryRepository:
    def __init__(self, db):
        self._db = db

    def add(self, d: Delivery) -> None:
        self._db.execute(f"INSERT INTO deliveries ({DELIVERY_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (d.id, d.rule_id, d.user_id, d.channel, d.recipient, d.message, d.status, d.provider_id, d.error,
                          d.created_at, d.sent_at))

    def get(self, delivery_id: str) -> Delivery | None:
        row = self._db.query_one(f"SELECT {DELIVERY_COLUMNS} FROM deliveries WHERE id = ?", (delivery_id,))
        return _delivery(row) if row else None

    def mark(self, delivery_id: str, status: str, provider_id: str | None = None, error: str | None = None,
             sent_at: str | None = None) -> None:
        self._db.execute("UPDATE deliveries SET status = ?, provider_id = ?, error = ?, sent_at = ? WHERE id = ?",
                         (status, provider_id, error, sent_at, delivery_id))

    def for_user(self, user_id: str, limit: int = 50) -> list[Delivery]:
        rows = self._db.query(f"SELECT {DELIVERY_COLUMNS} FROM deliveries WHERE user_id = ? ORDER BY created_at DESC, id DESC "
                              "LIMIT ?", (user_id, limit))
        return [_delivery(r) for r in rows]
