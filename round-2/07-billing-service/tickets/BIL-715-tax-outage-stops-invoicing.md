# BIL-715: A Taxly timeout stopped invoicing for most customers

**Type:** Bug · **Priority:** High · **Reporter:** Finance, SRE

## Description
Taxly was slow on 1 July (as it often is at the start of a month). One request timed out for the 12th customer in the run, and no
customers after it were invoiced: the job failed and was retried twice, failing again each time on a different customer. Finance
had to run invoices by hand for 300 customers. The README says a tax failure for one customer must not stop the others.

## Acceptance criteria
- If Taxly fails for a customer, that customer's invoice is created as `pending_tax` with tax 0, and the run continues.
- Customers for whom Taxly works are invoiced normally, with tax.
- The failure is visible in the logs.

## Out of scope
- Recalculating tax for `pending_tax` invoices later (BIL-716).
