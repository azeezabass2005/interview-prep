FIXES = [
    ("blike/db.py", "CREATE INDEX IF NOT EXISTS idx_requests_requester_key",
     "CREATE UNIQUE INDEX IF NOT EXISTS idx_requests_requester_key"),
    ("blike/errors.py", "class NotFound(DomainError):\n    pass\n",
     "class NotFound(DomainError):\n    pass\n\n\nclass DuplicateRequest(DomainError):\n    pass\n"),
    ("blike/repositories/requests.py", "from datetime import datetime\n", "import sqlite3\nfrom datetime import datetime\n"),
    ("blike/repositories/requests.py", "from ..db import Database\n", "from ..db import Database\nfrom ..errors import DuplicateRequest\n"),
    ("blike/repositories/requests.py",
     "    def insert(self, req: MeetingRequest) -> None:\n        with self._db.transaction() as conn:\n",
     "    def insert(self, req: MeetingRequest) -> None:\n        try:\n            self._insert(req)\n"
     "        except sqlite3.IntegrityError as e:\n            raise DuplicateRequest(req.idempotency_key) from e\n\n"
     "    def _insert(self, req: MeetingRequest) -> None:\n        with self._db.transaction() as conn:\n"),
    ("blike/services/scheduling.py", "from ..errors import ValidationError", "from ..errors import DuplicateRequest, ValidationError"),
    ("blike/services/scheduling.py",
     "        self._requests.insert(req)\n        self._notifier.request_received(req)\n",
     "        try:\n            self._requests.insert(req)\n        except DuplicateRequest:\n"
     "            return self._requests.find_by_key(requester, idempotency_key)\n"
     "        self._notifier.request_received(req)\n"),
    ("blike/services/availability.py", "    return a_start <= b_end and b_start <= a_end", "    return a_start < b_end and b_start < a_end"),
    ("blike/services/scoring.py", "    def sender_class(self, sender: str) -> str:\n",
     "    def sender_class(self, sender: str) -> str:\n        sender = sender.strip().lower()\n"),
    ("blike/services/scheduling.py", "chunk = pending[i:i + BATCH_SIZE - 1]", "chunk = pending[i:i + BATCH_SIZE]"),
]
