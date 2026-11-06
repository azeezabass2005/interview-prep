# BIL-701: 40 customers invoiced twice for June

**Type:** Bug · **Priority:** Critical · **Reporter:** Finance

## Description
On 1 July the worker host was restarted in the middle of the June invoice run. When it came back, the run started again from the
beginning, and every customer that had already been invoiced got a second June invoice. Some of them paid both. Retries and
re-runs are expected to happen; the invoice run has to cope with them.

## Acceptance criteria
- Running the invoice run for a period any number of times leaves each customer with exactly one invoice for that period.
- Customers that weren't invoiced before the interruption are invoiced when the run is retried.

## Out of scope
- Cleaning up the duplicate June invoices (Finance is voiding them by hand).
