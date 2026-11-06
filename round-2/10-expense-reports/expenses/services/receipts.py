from ..config import OCR_BATCH_SIZE


class ReceiptScanner:
    """The worker's `ocr_batch` job: reads the totals off queued receipts with Scanly. Scheduled every minute."""

    def __init__(self, expenses, scanly, queue, logger):
        self._expenses = expenses
        self._scanly = scanly
        self._queue = queue
        self._logger = logger

    def schedule(self) -> str:
        return self._queue.enqueue("ocr_batch", {}, max_attempts=3)

    def run(self, payload: dict) -> None:
        batch = self._expenses.receipts_with_status("queued", OCR_BATCH_SIZE)
        for row in batch:
            self._expenses.update(row["id"], receipt_status="processing")
        for row in batch:
            total = self._scanly.read_total(row["image_b64"])
            self._expenses.update(row["id"], receipt_status="done", receipt_total=total)
        self._logger.info("ocr_batch_done", count=len(batch))
