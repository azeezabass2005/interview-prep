from ..clock import iso
from ..schema import SECTORS


class DigestService:
    """The daily email of newly published research, one per client user who has it enabled."""

    def __init__(self, users, reports, entitlements, email, queue, clock, logger):
        self._users = users
        self._reports = reports
        self._entitlements = entitlements
        self._email = email
        self._queue = queue
        self._clock = clock
        self._logger = logger

    def schedule_all(self) -> int:
        recipients = self._users.digest_recipients()
        for user in recipients:
            self._queue.enqueue("send_digest", {"user_id": user.id}, max_attempts=4)
        return len(recipients)

    def send_digest(self, payload: dict) -> None:
        user = self._users.get(payload["user_id"])
        if user is None or not user.digest_enabled:
            return
        today = self._clock.now().date().isoformat()
        sectors = sorted(self._entitlements.sectors_for(user.org_id, today) & set(SECTORS))
        since = user.last_digest_at or "1970-01-01T00:00:00"
        new = self._reports.published_since(sectors, since)
        if not new:
            return
        self._users.set_last_digest(user.id, iso(self._clock.now()))
        lines = "".join(f"<li><b>{r.title}</b> ({r.sector}): {r.summary}</li>" for r in new)
        try:
            self._email.send(user.email, f"Your research digest: {len(new)} new reports", f"<ul>{lines}</ul>")
        except Exception as e:
            self._logger.error("digest_failed", user_id=user.id, error=str(e))
