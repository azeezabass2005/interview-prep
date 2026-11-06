# BIL-705: Usage at midnight on the 1st is billed in two months

**Type:** Bug · **Priority:** Medium · **Reporter:** Customer (Birch Capital)

## Description
Birch's finance team reconciles our invoices against their own API logs. Their June and July invoices together charge for 1,000
more API calls than they made. The difference is a single batch of 1,000 calls our metering pipeline recorded at exactly
2026-07-01T00:00:00 (it rounds batch times down to the minute), which appears in **both** invoices.

## Acceptance criteria
- Each usage event is billed in exactly one period: the one containing its timestamp, as defined in the README.
- Events at exactly midnight on the 1st belong to the new month.
