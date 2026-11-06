# EXP-1005: Foreign-currency expenses converted at the wrong date's rate

**Type:** Bug · **Priority:** Medium · **Reporter:** Finance

## Description
Eli's Berlin trip report has two euro expenses: a hotel on 2 June and a dinner on 18 June. Both were converted at 1.08, which
was the rate on 2 June. On 18 June the rate was 1.15. Finance checks a sample of reports against Ratesy every month and found
many like this: the second and later expenses in the same currency within a day get the first one's rate.

## Acceptance criteria
- Each expense is converted at the rate for its own date.
- Rates are still cached (Ratesy charges per call): two expenses in the same currency on the same date make one Ratesy call.
