from collections import defaultdict
from typing import Dict, List, Optional

from .models import Shift, Worker


class InMemoryStore:
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self.shifts: Dict[str, List[Shift]] = defaultdict(list)

    def worker(self, worker_id: str) -> Optional[Worker]:
        return self.workers.get(worker_id)
