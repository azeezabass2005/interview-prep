# Portfolio Rebalancer

A robo-advisor periodically brings each client portfolio back to its target allocation. The code in `rebalance/` produces the list of
trades. Advisors say some plans are wrong.

## Rules

- **Total value** = cash + Σ shares × price.
- **Cash buffer:** **2%** of total value always stays in cash. Targets apply to the **investable** 98%:
  target value = target weight × total value × 0.98.
- **Tolerance band:** a holding is traded only if |target value − current value| is **more than 5% of total value**.
- **Whole shares:** trade quantity = (target value − current value) ÷ price, **rounded toward zero**
  (never overshoot the target in either direction).
- **Order:** all **sells first** (they raise cash), then **buys, largest dollar underweight first**.
- **Cash limit:** a buy may only spend cash above the buffer (cash − 2% of total value). Buy fewer shares if needed.
- Trades worth less than **$100** are skipped.

## Example

Cash $2,000 · AAA 100 @ $50 ($5,000) · BBB 10 @ $300 ($3,000) → total $10,000, investable $9,800.
Targets AAA 40% → $3,920, BBB 60% → $5,880.

- AAA: −$1,080 (> $500 band) → −21.6 → **SELL 21** → cash $3,050
- BBB: +$2,880 → 9.6 → **BUY 9** ($2,700; cash above buffer is $2,850) → cash $350

Plan: **SELL AAA 21, BUY BBB 9**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model the portfolio, targets and trades.
3. Outline the planning algorithm and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
