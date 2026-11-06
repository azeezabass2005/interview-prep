# BLT-420: Amending a trade with quantity 0 returns 500 and pages on-call

**Type:** Bug · **Priority:** Medium · **Reporter:** SRE

## Description
On-call was paged three times last week for `500 Internal Server Error` on `PATCH /trades/{id}`. Each time a trader had typed 0
(or a negative price) in the amend form. The web app shows "Something went wrong" instead of telling them what was wrong. Booking
a trade with quantity 0 correctly gives a 400.

## Acceptance criteria
- Invalid amendments (quantity not 1–5,000, price not positive, amending a cancelled trade) return `400` with a clear message.
- Unexpected errors are still 500s.
