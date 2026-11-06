# EXP-1001: Managers can approve reports from other teams

**Type:** Security · **Priority:** High · **Reporter:** Internal Audit

## Description
Audit found 23 reports in Q2 approved by a manager who isn't the employee's manager. In one case two managers approved each other's
team members' inflated taxi claims. Managers need to *view* reports across the organisation when covering for each other, but
approving must stay with the employee's own manager.

## Acceptance criteria
- Only the employee's own manager can approve or reject their report; any other manager gets 403 and nothing changes.
- Viewing rules and the no-self-approval rule are unchanged.
