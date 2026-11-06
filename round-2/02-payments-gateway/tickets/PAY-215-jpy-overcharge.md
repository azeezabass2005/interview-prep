# PAY-215: Japanese customers charged 100 times the price

**Type:** Bug · **Priority:** Critical · **Reporter:** Merchant Support (Kyoto Tea House)

## Description
Kyoto Tea House went live with us yesterday. A customer buying tea for ¥1,500 was charged ¥150,000. Our dashboard and the API
response both say the payment was ¥1500, but Paystream's dashboard says ¥150,000. They've switched us off until it's fixed. USD,
GBP and EUR merchants are fine.

## Steps to reproduce
1. `POST /payments` with `{"amount": "1500", "currency": "JPY", ...}`.
2. The response says `"amount": "1500"`, but the charge sent to Paystream is for 150000.

## Acceptance criteria
- Every supported currency is sent to Paystream in its correct minor unit (JPY has none, KWD has three decimal places).
- Amounts with more decimal places than the currency allows are still rejected.
- What we store, return and send to Paystream agree.
