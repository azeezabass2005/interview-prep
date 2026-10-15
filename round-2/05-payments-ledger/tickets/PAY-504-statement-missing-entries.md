# PAY-504: Statement is missing transactions

**Type:** Bug · **Reporter:** Corporate clients · **Priority:** Medium

## Description
A corporate client pays salaries in bulk (hundreds of transfers in the same second). Their statement export, which pages through
`GET /accounts/{id}/statement?cursor=…`, has fewer rows than their payment file. Paging with a large page size shows everything.

## Acceptance criteria
- Paging through a statement returns every entry exactly once, whatever the page size and even when many entries share a timestamp.

## Out of scope
- CSV export format.
