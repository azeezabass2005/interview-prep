from .db import Database
from .ids import new_id
from .models import MeetingRequest


class Notifier:
    """Writes emails to the outbox table; a separate mailer process sends them."""

    def __init__(self, db: Database, clock):
        self._db = db
        self._clock = clock

    def request_received(self, req: MeetingRequest) -> None:
        self._write(req.sender, f"Request received: {req.title}",
                    f"Your request ({req.request_id}) is in Blike's queue.")

    def request_scheduled(self, req: MeetingRequest, start) -> None:
        self._write(req.sender, f"Scheduled: {req.title}", f"Blike will see you at {start:%a %d %b %H:%M}.")

    def _write(self, recipient: str, subject: str, body: str) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO outbox (message_id, recipient, subject, body, created_at) VALUES (?, ?, ?, ?, ?)",
                (new_id("msg"), recipient, subject, body, self._clock.now().isoformat()),
            )

    def pending_count(self) -> int:
        with self._db.transaction() as conn:
            return conn.execute("SELECT COUNT(*) FROM outbox WHERE sent = 0").fetchone()[0]
