# BIL-720: Invoices show the same payment twice

**Type:** Bug · **Priority:** High · **Reporter:** Customer Support

## Description
Several customers' invoices list the same payment twice, and some invoices show as overpaid, which triggers automatic refund
reviews. Paygate's logs show they delivered those `payment.succeeded` webhooks twice (their first delivery timed out on their side,
though we had processed it). Paygate says redeliveries are normal and we must handle them.

## Acceptance criteria
- A payment is recorded once per Paygate `payment_id`, however many times the webhook arrives.
- Redelivered webhooks still get `200` (so Paygate stops retrying).
- Different payments for the same invoice (partial payments) still add up.
