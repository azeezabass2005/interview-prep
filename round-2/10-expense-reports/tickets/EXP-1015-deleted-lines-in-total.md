# EXP-1015: Report total includes deleted expenses

**Type:** Bug · **Priority:** High · **Reporter:** Employee help desk, Payroll

## Description
Eli deleted a duplicated $1,200 flight from his report. It disappeared from the list of expenses, but the report total still
includes it, and Payroll pays the report total. Another employee can't submit a $300 report because it "is over $25,000": they had
added a $30,000 line by mistake (typed cents as dollars) and deleted it.

## Acceptance criteria
- Deleted lines don't count in a report's total, nor in the submission limit.
- Deleted lines are still kept in the database.
