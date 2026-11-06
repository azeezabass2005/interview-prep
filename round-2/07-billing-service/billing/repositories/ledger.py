class CustomerRepository:
    def __init__(self, db):
        self._db = db

    def add(self, customer_id: str, name: str, country: str, seats: int, seat_price_cents: int) -> None:
        self._db.execute("INSERT INTO customers (id, name, country, seats, seat_price_cents) VALUES (?, ?, ?, ?, ?)",
                         (customer_id, name, country, seats, seat_price_cents))

    def get(self, customer_id: str):
        return self._db.query_one("SELECT * FROM customers WHERE id = ?", (customer_id,))

    def active(self) -> list:
        return self._db.query("SELECT * FROM customers WHERE active = 1 ORDER BY id")

    def set_seats(self, customer_id: str, seats: int) -> None:
        self._db.execute("UPDATE customers SET seats = ? WHERE id = ?", (seats, customer_id))


class UsageRepository:
    def __init__(self, db):
        self._db = db

    def record(self, event_id: str, customer_id: str, quantity: int, occurred_at: str) -> None:
        self._db.execute("INSERT OR IGNORE INTO usage_events (id, customer_id, quantity, occurred_at) VALUES (?, ?, ?, ?)",
                         (event_id, customer_id, quantity, occurred_at))

    def total(self, customer_id: str, start: str, end: str) -> int:
        row = self._db.query_one(
            "SELECT COALESCE(SUM(quantity), 0) AS n FROM usage_events "
            "WHERE customer_id = ? AND occurred_at BETWEEN ? AND ?",
            (customer_id, start, end),
        )
        return row["n"]


class ChargeRepository:
    def __init__(self, db):
        self._db = db

    def add(self, charge_id: str, customer_id: str, description: str, amount_cents: int, created_at: str) -> None:
        self._db.execute("INSERT INTO charges (id, customer_id, description, amount_cents, created_at) VALUES (?, ?, ?, ?, ?)",
                         (charge_id, customer_id, description, amount_cents, created_at))

    def uninvoiced(self, customer_id: str, before: str) -> list:
        return self._db.query("SELECT * FROM charges WHERE customer_id = ? AND invoice_id IS NULL AND created_at < ? "
                              "ORDER BY created_at, id", (customer_id, before))

    def for_customer(self, customer_id: str) -> list:
        return self._db.query("SELECT * FROM charges WHERE customer_id = ? ORDER BY created_at, id", (customer_id,))


class InvoiceRepository:
    def __init__(self, db):
        self._db = db

    def create(self, invoice: dict, lines: list[tuple[str, int]], charge_ids: list[str]) -> None:
        with self._db.transaction() as conn:
            conn.execute("INSERT INTO invoices (id, customer_id, period, subtotal_cents, tax_cents, total_cents, status, "
                         "created_at) VALUES (:id, :customer_id, :period, :subtotal_cents, :tax_cents, :total_cents, :status, "
                         ":created_at)", invoice)
            for i, (description, amount) in enumerate(lines):
                conn.execute("INSERT INTO invoice_lines (invoice_id, position, description, amount_cents) VALUES (?, ?, ?, ?)",
                             (invoice["id"], i, description, amount))
            for charge_id in charge_ids:
                conn.execute("UPDATE charges SET invoice_id = ? WHERE id = ?", (invoice["id"], charge_id))

    def get(self, invoice_id: str):
        return self._db.query_one("SELECT * FROM invoices WHERE id = ?", (invoice_id,))

    def find(self, customer_id: str, period: str):
        return self._db.query_one("SELECT * FROM invoices WHERE customer_id = ? AND period = ?", (customer_id, period))

    def for_customer(self, customer_id: str) -> list:
        return self._db.query("SELECT * FROM invoices WHERE customer_id = ? ORDER BY period DESC, created_at DESC",
                              (customer_id,))

    def lines(self, invoice_id: str) -> list:
        return self._db.query("SELECT description, amount_cents FROM invoice_lines WHERE invoice_id = ? ORDER BY position",
                              (invoice_id,))

    def set_status(self, invoice_id: str, status: str) -> None:
        self._db.execute("UPDATE invoices SET status = ? WHERE id = ?", (status, invoice_id))


class PaymentRepository:
    def __init__(self, db):
        self._db = db

    def add(self, payment_id: str, invoice_id: str, provider_payment_id: str, amount_cents: int, at: str) -> None:
        self._db.execute("INSERT INTO payments (id, invoice_id, provider_payment_id, amount_cents, received_at) "
                         "VALUES (?, ?, ?, ?, ?)", (payment_id, invoice_id, provider_payment_id, amount_cents, at))

    def by_provider_id(self, provider_payment_id: str):
        return self._db.query_one("SELECT * FROM payments WHERE provider_payment_id = ?", (provider_payment_id,))

    def paid_total(self, invoice_id: str) -> int:
        return self._db.query_one("SELECT COALESCE(SUM(amount_cents), 0) AS n FROM payments WHERE invoice_id = ?",
                                  (invoice_id,))["n"]

    def for_invoice(self, invoice_id: str) -> list:
        return self._db.query("SELECT * FROM payments WHERE invoice_id = ? ORDER BY received_at, id", (invoice_id,))
