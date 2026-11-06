# EDGE-910: Customers' API tokens are sent to FX Partner

**Type:** Security · **Priority:** Critical · **Reporter:** FX Partner's security team

## Description
FX Partner's security team emailed us: their access logs contain `Authorization: Bearer tok_…` headers from our gateway, alongside
our partner key. Those are our customers' API tokens. Anyone at FX Partner with log access (or anyone who breaches them) could call
our API as our customers.

## Acceptance criteria
- Requests to external upstreams carry no client credentials: no `Authorization` header (and no cookies).
- FX Partner still gets our partner key, and internal upstreams are unchanged.

## Out of scope
- Rotating the exposed tokens (Security is doing it).
