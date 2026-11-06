# R2-02 · Payments Gateway: Interviewer Guide

A ~800-line Python API (no framework) that takes card payments for merchants through a third-party processor ("Paystream") and
applies its webhooks. Five tickets, each a different real integration/back-end failure. The candidate picks one; one ticket done
properly with a test is a full pass. `web/` (Next.js dashboard) is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| PAY-201 double charges | Third-party adapter / retries | `Idempotency-Key: uuid4()` is generated **inside** the retry loop, so a retry after a timeout is a new request to Paystream | `adapters/paystream.py: _post` | Lowering retries or the timeout; de-duplicating in our DB (our side already has one payment; the duplicate is at Paystream) |
| PAY-205 retried declines | Adapter / error classification | `if result.status >= 400: continue` retries 4xx too | `adapters/paystream.py: _post` | Special-casing 402 only (AC: any 4xx); breaking 5xx retries |
| PAY-210 webhooks rejected | Security / adapters | HMAC is computed over `json.dumps(json.loads(body), separators=…)` instead of the **raw bytes**; pretty-printed bodies re-serialise differently | `adapters/webhooks.py: verify` | Re-serialising with `indent=2` (works for v2, breaks v1); turning off verification; comparing with `==` instead of `compare_digest` |
| PAY-215 JPY overcharge | Money / adapter contract | `to_minor` multiplies by 100 for every currency; the exponent table exists but isn't used for the conversion (`to_major` is right, so responses look right) | `money.py: to_minor` | Patching JPY only; fixing the display instead of the amount sent |
| PAY-220 outage → 500 | Error handling / middleware | `PaystreamUnavailable` is a plain `Exception`; the service only catches `PaystreamDeclined`, so it escapes as a 500 and the row stays `processing` | `services/payments.py: create` | Making the error middleware turn *every* exception into 503 (other bugs would then be retried by SDKs); setting the header in the handler only |

## PM answers
| Question | Answer |
|---|---|
| Is Paystream's idempotency window enough for our retries? | Yes, 24 hours; our retries are seconds apart. |
| What key should we send Paystream? | Your call; it must be stable for one payment (or refund) across retries. Using our payment id is fine. |
| Which Paystream responses are final? | Any 4xx is final (declines, validation errors). 5xx, timeouts and connection errors are retryable. 429 is out of scope. |
| Should declines be 4xx to the merchant? | No: keep 201 with `status: failed` and the code; the payment was created. |
| How are webhooks signed? | As in the README: HMAC-SHA256 over `<t>.<raw body>`. Paystream doesn't promise any particular JSON formatting. |
| Which currencies matter? | Everything in `CURRENCY_EXPONENT`; KWD is coming next month. |
| After a 503, can the merchant retry with the same Idempotency-Key? | Out of scope for this ticket: the AC says the payment shows `failed/processor_unavailable`; the SDK retries with a new key. Good candidates point out the trade-off. |
| Retry-After value? | 30 seconds. |

## PAY-201 · stable idempotency key
**Fix:** pass a key into `_post` and use it for every attempt, e.g. `create_charge` → `_post("/charges", payload, f"charge-{payment_id}")`,
`create_refund` → `f"refund-{refund_id}"`.
**Test:** FakeTransport queues `TransportTimeout`, then success → two calls, **same** `Idempotency-Key`, one payment `captured`.
Strong: explains at-least-once delivery over an unreliable network, and that idempotency must be end to end (merchant key → our
payment → Paystream key). Bonus: notices the key should not be random even across process restarts.

## PAY-205 · don't retry 4xx
**Fix:** retry only on `status >= 500` (and transport errors); return/raise immediately on 4xx.
**Test:** queue one 402 `card_declined` → exactly one call, payment `failed`, `failure_code == "card_declined"`. Also 503 then 200 →
two calls, captured. Strong: "retry only what's transient and safe; classify errors at the boundary".

## PAY-210 · sign the raw body
**Fix:** `sign(secret, timestamp, body)` on the raw bytes, then parse JSON after verifying.
**Test:** pretty-printed body (`json.dumps(event, indent=2)`) correctly signed → 200 and payment captured; the same body with one
byte changed → 401. Strong: "never verify a signature over a re-encoding"; parse after verify; `compare_digest` is already there.

## PAY-215 · minor units
**Fix:** `return int(value * (Decimal(10) ** exponent))` (or `scaleb`).
**Test:** JPY "1500" → Paystream gets `amount: 1500`, response `amount_minor: 1500`, `amount: "1500"`; KWD "1.250" → 1250;
JPY "15.5" still 400.

## PAY-220 · processor unavailable
**Fix (in the service):** `except PaystreamUnavailable:` mark the payment `failed` with `failure_code="processor_unavailable"`,
then `raise ServiceUnavailable("payment processor unavailable, retry later", retry_after=30)`. The error middleware already sets
`Retry-After` from `retry_after`.
**Test:** three `TransportTimeout`s → 503, `Retry-After: 30`, error code `service_unavailable`, and the payment (via `GET /payments`)
is `failed/processor_unavailable`; no secret key or traceback in the response body.

## Red herrings
- Our `payments` table already has `UNIQUE (merchant_id, idempotency_key)` and the merchant-level replay works.
- The webhook timestamp tolerance check is correct; so is the event-id de-duplication.
- `to_major` is correct (which is why the API response looks right in PAY-215).

## Questions about the candidate's fixes (data structures)
- "Two API instances receive the same merchant retry at the same moment. What happens?" (Both miss `by_key`; one insert wins the
  UNIQUE index, the other gets `Conflict` → 409. Better: catch it and return the winner's row, as in the calendar exercise.)
- "How long must the webhook event-id table keep rows?" (At least Paystream's redelivery window, e.g. 3 days; then prune by
  `received_at` with an index, or a TTL store.)
- "Why integers for money?" (Binary floats can't represent 0.1; minor units with an exponent table are exact; Decimal for parsing.)
- "Retry policy: what would you add?" (Exponential backoff with jitter, a total deadline, a circuit breaker so an outage fails fast.)

## Feature requests
1. **"Retries after PAY-220 should reuse the same Idempotency-Key."** Strong: a `processor_unavailable` payment can be retried in
   place; state machine `failed(processor_unavailable) → processing`; keep Paystream's key stable so a late success isn't doubled.
2. **"Merchant webhooks: notify merchants when a payment changes."** Strong: outbox table written in the same transaction, a job
   that delivers with signatures and retries, at-least-once semantics, event ids for merchant-side de-duplication.
3. **"Partial captures."** Strong: authorise then capture ≤ authorised amount; new states; refund maths changes.

## Scoring signals
- **Strong:** reproduces with FakeTransport scripts (timeout then success, 402, pretty JSON) through `POST /payments`; explains the
  failure in terms of what Paystream saw; keeps fixes in the adapter layer for adapter bugs.
- **Weak:** fixes by changing timeouts/retry counts; disables signature checks; adds `except Exception: return 503` in middleware;
  no failing test first.
