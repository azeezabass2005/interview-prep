# Dividend Reinvestment (DRIP)

A broker pays dividends to its clients. Clients can enrol a holding in the **dividend reinvestment plan (DRIP)**, which uses the
dividend to buy more shares of the same stock. `drip.py` records holdings and enrolments and processes dividend payments.

## Holdings

Shares are recorded as dated trades (buys positive, sells negative; fractional shares allowed). A client can't sell more than they hold.

## Paying a dividend

A dividend has a symbol, an amount per share, a **record date**, a **pay date** and a reinvestment price.

1. **Eligibility:** the shares a client holds at the end of the **record date** (trades dated on or before it). Clients with no shares get nothing.
2. **Gross** = shares × amount per share, rounded **down** to the cent.
3. **Withholding tax** by the client's country of residence: US 0%, CA 15%, GB 0%, **any other country 30%**. Rounded to the nearest cent.
4. **Net** = gross − tax.
5. If the holding is **enrolled in DRIP as of the record date**, net is used to buy shares at the reinvestment price. Shares are bought in
   units of 0.0001, **rounding down** (never spend more than net). The shares are added on the pay date. **Cash left over is paid out**,
   rounded down to the cent.
6. Otherwise net is paid out in cash.

## Enrolment

Clients enrol or leave the plan per holding. A change made on date D applies to dividends whose record date is on or after D.

## Reports

- `holdings(account, on)`: shares per symbol held at the end of a date (symbols with zero shares are left out).
- `statement(account)`: every dividend payment of the account.
- `tax_summary(account, year)`: totals of gross, tax withheld, reinvested shares and cash for payments with a pay date in that year.

## Example

US client, 100 shares, enrolled. $0.50 per share, reinvestment price $25.00 → gross $50.00, tax $0.00, **2.0000 shares**, cash $0.00.
