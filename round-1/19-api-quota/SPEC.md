# API Quota

A market-data company sells API access. Every API key is on a plan that limits **bursts** (with a token bucket) and **monthly volume**.
`quota.py` decides whether a request is allowed and produces monthly invoices.

## Plans

| Plan | Bucket capacity | Refill (tokens/s) | Monthly units | Price |
|---|---|---|---|---|
| FREE | 10 | 5 | 1,000, **hard limit** | $0 |
| PRO | 50 | 20 | 100,000 included | $49.00 + **$0.002 per unit above 100,000** |

## Requests

- A request has a **cost** in units (1 for a quote, N for a batch of N symbols). It needs `cost` tokens.
- **Token bucket:** a new key starts with a full bucket. Tokens refill continuously at the plan's rate and never exceed capacity.
- If there aren't enough tokens, the request is rejected with **429** and nothing changes (no tokens taken, no usage counted).
- **FREE keys:** a request that would take the month's usage **above 1,000 units** is rejected with **429**.
- Allowed requests return **200** and add their cost to the key's usage for the **calendar month (UTC)**. Usage starts from zero every month.
- Unknown keys get **403**.

## Invoices

For a month: FREE $0.00; PRO $49.00 + overage units × $0.002, rounded to the cent.

## Example

FREE key at 12:00:00: cost 8 → 200 (2 tokens left). At 12:00:01 (7 tokens): cost 6 → 200.
