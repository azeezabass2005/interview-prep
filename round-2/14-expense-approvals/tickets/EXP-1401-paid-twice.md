# EXP-1401: Expense reimbursed twice

**Type:** Bug · **Reporter:** Accounts payable · **Priority:** Critical

## Description
An employee was reimbursed twice for the same $640 hotel bill. The approval audit shows two approvals by the same manager within 200 ms
(double-click in the web app; the requests hit different instances).

## Acceptance criteria
- However many concurrent approval requests arrive, an expense moves `SUBMITTED → APPROVED` once and produces **one** payment.
- The losing request gets 409.

## Out of scope
- Disabling the button after click.
