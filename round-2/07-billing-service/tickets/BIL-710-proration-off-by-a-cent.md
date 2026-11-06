# BIL-710: Prorated seat charges are sometimes a cent off

**Type:** Bug · **Priority:** Low · **Reporter:** Finance

## Description
Finance's reconciliation spreadsheet disagrees with our prorated charges on some seat changes, always by one cent, always with us
lower. Example: Birch added 3 seats ($49.99 each) on 16 June. 3 × 4,999 × 15 ÷ 30 = 7,498.5 cents, which should round up to
$74.99. We charged $74.98. The auditors want our calculation to follow the documented rule exactly.

## Acceptance criteria
- Prorated charges are computed exactly in integer cents and rounded half up, as in the README.
- Results that don't involve half a cent are unchanged.
