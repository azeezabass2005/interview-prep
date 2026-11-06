# EXP-1020: Employee edited the reimbursement amount directly

**Type:** Security · **Priority:** Critical · **Reporter:** Internal Audit

## Description
An expense line shows a €40 lunch, but it was reimbursed $4,000. The audit log shows the employee called
`PATCH /expenses/{id}` with `{"usd_cents": 400000}` from a script while the report was a draft, then submitted it. The manager
approved the report because the line said €40 and the receipt said €40.

## Acceptance criteria
- Only merchant, category, amount, currency and date can be changed through the API; `usd_cents` is always recalculated by the
  service.
- A request that tries to change any other field is rejected with 400 and changes nothing.
