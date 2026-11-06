# PAY-220: During Paystream's outage merchants got 500s and payments stuck "processing"

**Type:** Bug · **Priority:** High · **Reporter:** Merchant Support

## Description
Paystream was down for 25 minutes on Sunday. Our API answered `POST /payments` with `500 Internal Server Error`, so merchant SDKs
(which only retry `503` with `Retry-After`) gave up and showed customers "something went wrong". Afterwards about 300 payments
were stuck in `processing`, so merchants couldn't tell whether customers had paid, and support had to check each one against
Paystream.

## Acceptance criteria
- When Paystream can't be reached after our retries, the API answers `503` with a `Retry-After` header (30 seconds) and the usual
  error body, so SDKs retry.
- The payment doesn't stay `processing`: it's `failed` with `failure_code: "processor_unavailable"`, so the merchant can see what
  happened.
- Declines and successful charges behave as before.

## Out of scope
- A status page integration.
