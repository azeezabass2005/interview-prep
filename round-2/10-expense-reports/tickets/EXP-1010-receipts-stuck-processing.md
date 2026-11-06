# EXP-1010: Receipts stuck in "processing" forever

**Type:** Bug · **Priority:** High · **Reporter:** Employee help desk

## Description
Dozens of employees see "Reading receipt…" for days. Managers won't approve reports until the receipt totals show. The worker's
dead-letter queue has `ocr_batch` jobs that failed with "ScanlyError: receipt is unreadable". It seems one blurry photo is enough
to block everyone else's receipts in the same batch, permanently.

## Acceptance criteria
- An unreadable receipt is marked `failed` with Scanly's reason; the rest of the batch is processed normally.
- No receipt stays in `processing` after the job finishes.
- If Scanly is temporarily unavailable, affected receipts are retried later rather than marked failed.
