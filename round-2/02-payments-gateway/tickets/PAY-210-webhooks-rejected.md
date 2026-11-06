# PAY-210: Payments stuck in "pending" since Paystream's webhook update

**Type:** Bug · **Priority:** High · **Reporter:** Merchant Support

## Description
Since Paystream rolled out "webhooks v2" on Monday, payments that need asynchronous confirmation (3-D Secure, bank transfers) stay
`pending` forever. Paystream's dashboard shows every webhook delivery to us failing with `401 bad webhook signature` and being
retried. Their changelog says v2 payloads are "pretty-printed JSON with the same fields". Our signing secret hasn't changed, and
the timestamps are fine.

## Steps to reproduce
1. Create a payment that Paystream leaves pending.
2. Paystream sends a correctly signed `charge.succeeded` webhook whose body is pretty-printed JSON.
3. We reply 401 and the payment stays pending.

## Acceptance criteria
- Correctly signed webhooks are accepted however the JSON is formatted.
- Webhooks with a wrong signature, a tampered body or a stale timestamp are still rejected.

## Out of scope
- Replaying the failed deliveries (Paystream will redeliver once we return 2xx).
