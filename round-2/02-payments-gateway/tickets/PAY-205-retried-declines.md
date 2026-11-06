# PAY-205: Paystream warning: we're retrying declined cards

**Type:** Bug · **Priority:** High · **Reporter:** Payments Partnerships

## Description
Paystream's risk team emailed us: our account retries **declined** charges two more times within a second. Card networks treat
that pattern like card testing, and they've threatened to raise our fees. Some customers also complained their bank sent three
"declined" texts for one purchase, and one customer said the purchase went through on the third try after their bank's fraud
check had declined it.

## Steps to reproduce
1. Charge a card that Paystream declines (`402`, `{"error": {"code": "card_declined"}}`).
2. We send the same charge to Paystream three times.

## Acceptance criteria
- A decline (any `4xx` from Paystream) is not retried; the payment is `failed` with Paystream's code (e.g. `card_declined`).
- Timeouts, connection errors and `5xx` are still retried as today.

## Out of scope
- Showing decline reasons to end customers.
