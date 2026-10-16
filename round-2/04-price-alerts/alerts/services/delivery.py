from ..config import DELIVERY_BATCH_SIZE
from ..db import Database
from ..repositories.deliveries import DeliveryRepository


class DeliveryWorker:
    def __init__(self, db: Database, clock, sender, worker_id: str):
        self._deliveries = DeliveryRepository(db)
        self._clock = clock
        self._sender = sender
        self.worker_id = worker_id

    def run_once(self) -> int:
        sent = 0
        for d in self._deliveries.pending_due(self._clock.now(), DELIVERY_BATCH_SIZE):
            self._sender.send(d.user_id, d.message)
            self._deliveries.mark_sent(d.delivery_id, self.worker_id, self._clock.now())
            sent += 1
        return sent
