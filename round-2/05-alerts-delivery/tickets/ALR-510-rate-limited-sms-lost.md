# ALR-510: Alerts lost when Textwire rate-limits us

**Type:** Bug · **Priority:** High · **Reporter:** Customer Support

## Description
At the market open a burst of alerts fire at once. Textwire answers some of our requests with `429 Too Many Requests` and a
`Retry-After` header, and those alerts are never sent: the deliveries show `failed` with "provider rejected the message (429)".
Textwire's docs say a 429 means "slow down and try again".

## Acceptance criteria
- Deliveries that Textwire or Postbox rate-limit (429) are retried, not failed.
- Messages a provider permanently rejects (other 4xx, e.g. an invalid number) still fail without retries.

## Out of scope
- Honouring the exact `Retry-After` value (nice to have; our backoff is acceptable for now).
