# BLT-401: Desk head amended another desk's trade

**Type:** Bug · **Priority:** Critical · **Reporter:** Compliance

## Description
The audit log shows that Ray (rates desk head) changed the quantity of an FX trade on Tuesday. He says he typed a trade id from
an email and didn't notice it was FX. Desk heads must only be able to change their own desk's trades; Compliance needs to know how
this was possible and that it can't happen again.

## Acceptance criteria
- A desk head can amend trades on their own desk only; anyone else's attempt is refused (403) and changes nothing.
- Desk heads can still look up other desks' trades by id (they use it in risk reviews).
- Traders' and compliance's permissions are unchanged.
