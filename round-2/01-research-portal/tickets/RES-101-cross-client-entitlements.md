# RES-101: Clients can open research they don't subscribe to

**Type:** Bug · **Priority:** Critical · **Reporter:** Client Services

## Description
Hartwell Capital subscribes to **Energy** only (term subscription, renews each January). Their analyst opened a **Tech** report
yesterday from a link a colleague at another firm sent her, and it loaded. She can also see Tech reports in her list. Sales says
this started "a few weeks ago", around when Norland Partners signed our first open-ended (no end date) Tech subscription.

## Steps to reproduce
1. Firm A: Energy subscription, 2026-01-01 to 2027-01-01. Firm B: Tech subscription from 2026-01-01, no end date.
2. A Tech report is published.
3. A Firm A user requests `GET /reports/{id}` for it: 200 (expected 403). It also appears in Firm A's `GET /reports`.

## Acceptance criteria
- A firm's users can only see sectors their own firm is entitled to, whatever other firms subscribe to.
- Open-ended subscriptions still work for the firm that has them.
- A test proves one firm's open-ended subscription doesn't leak to another firm.

## Out of scope
- Re-checking entitlement on cached PDFs that clients already downloaded.
