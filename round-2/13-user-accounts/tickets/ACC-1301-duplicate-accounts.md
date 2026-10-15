# ACC-1301: Customers end up with two accounts

**Type:** Bug · **Reporter:** Client onboarding · **Priority:** High

## Description
Several clients have two accounts, e.g. `ann@example.com` and `Ann@Example.com`. The mobile app auto-capitalises the first letter, and
some users paste their address with a trailing space. Their data is split across the two accounts.

## Acceptance criteria
- Signing up with an address that differs from an existing one only in case or surrounding spaces is rejected (409).
- Logging in works whatever case or surrounding spaces the user types.

## Out of scope
- Merging existing duplicate accounts.
