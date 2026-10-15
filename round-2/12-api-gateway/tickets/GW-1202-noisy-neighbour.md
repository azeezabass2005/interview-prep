# GW-1202: One tenant's traffic throttles another tenant

**Type:** Bug · **Reporter:** Customer success · **Priority:** High

## Description
Globex's `admin` user started getting 429s at 09:00 every day. That's exactly when Acme's batch job (also running as a user named
`admin`) starts. Globex barely sends any traffic.

## Acceptance criteria
- Users with the same name in different tenants have independent limits.

## Out of scope
- Renaming users.
