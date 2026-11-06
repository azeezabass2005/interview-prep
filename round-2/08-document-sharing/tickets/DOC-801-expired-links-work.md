# DOC-801: Expired share links still open documents

**Type:** Security · **Priority:** Critical · **Reporter:** Compliance

## Description
A banker shared a draft term sheet with a client using a 48-hour link in March. The client's new analyst opened it last week,
months later, from an old email. The link was never revoked, but it should have expired after 48 hours. Every link we checked
works past its expiry.

## Acceptance criteria
- A share link stops working at its `expires_at`, with the same response as a revoked link.
- Links that haven't expired, and revocation, work as today.
