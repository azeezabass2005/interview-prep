# Expense Approvals

Employees submit expense reports that go through an approval chain. `expenses.py` validates reports and runs the approval workflow.

## Reports

- A report has items (category, amount, whether a receipt is attached). Items of **$25.00 or more** need a receipt.
- **Policy limits** per item: MEALS $75, HOTEL $250, TAXI $100. An item over its limit needs a written justification.

## Approval chain (by report total)

| Total | Approvers, in order |
|---|---|
| up to and including $500 | the submitter's manager |
| over $500 up to $5,000 | manager, then the director |
| over $5,000 | manager, director, then the CFO |

- Approvals happen **in order**: only the **next** approver in the chain can approve or reject.
- **Nobody approves their own report**: a step whose approver is the submitter is **skipped**.
- A rejection ends the report (REJECTED). The submitter can edit it and **resubmit**, and the chain **starts again from the first step**.
- When every step has approved, the report is APPROVED.

## Example

Ana (manager Mo; director Dina) submits $620 → chain **Mo → Dina**. Mo approves, Dina approves → **APPROVED**.
