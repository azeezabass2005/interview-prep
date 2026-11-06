# ALR-515: Customers can see other customers' alerts

**Type:** Security · **Priority:** Critical · **Reporter:** Bug bounty report

## Description
A researcher reports that any logged-in customer can call `GET /rules?user_id=<someone else>` and get that person's alerts:
symbols, thresholds and whether they're SMS or email. The parameter exists for our support team's tool. User ids are visible in
shared alert links, so they aren't secret.

## Acceptance criteria
- A customer can only list their own alerts; asking for another user's returns 403.
- Support staff can still look up alerts for customers in their own organisation, but not in other organisations.
