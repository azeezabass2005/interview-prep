# LNK-701: Our campaign alias now sends people to someone else's page

**Type:** Bug (security) · **Reporter:** Marketing · **Priority:** Critical

## Description
Marketing created `bbg.link/SummerSale` for a campaign. Last week visitors started landing on an unrelated personal blog. Someone else
created `bbg.link/summersale`, and now both spellings redirect to the blog.

## Steps to reproduce
1. Create alias `SummerSale` → https://www.bloomberg.example/summer.
2. Another user creates alias `summersale` → https://blog.example/me. Creation succeeds.
3. `GET /SummerSale` redirects to the blog.

## Acceptance criteria
- Creating an alias that differs from an existing one only by case is rejected (409).
- Existing aliases keep redirecting to their original target.

## Out of scope
- Cleaning up existing conflicting aliases in production (ops script).
