# IPO Allocation

An underwriter collects orders for a new share offering, closes the book, then allocates shares.
The offering is often **oversubscribed** (more shares requested than offered). The code in `ipo/` implements the rules below.

## Rules

- **Lot size:** shares trade in lots of **100**. Orders must be a positive multiple of 100. Allocations are always whole lots.
- **Book:** orders are accepted until the book is **closed**; later orders are rejected.
- **Undersubscribed** (total demand ≤ offering): everyone gets what they asked for.
- **Oversubscribed:** allocate in three steps:
  1. **Guarantee:** in **order-arrival sequence**, each investor gets **one lot**, while shares remain.
  2. **Pro-rata:** the remaining shares are split in proportion to each investor's **remaining demand**
     (request minus what they already got), **rounded down** to whole lots.
  3. **Leftover lots** are handed out **one lot at a time** to the investor with the **largest unfilled demand**.
     Ties go to the **earliest** order. Recompute after every lot.
- Nobody ever receives more than they requested, and the total allocated never exceeds the offering.

## Example

Offering 10,000 shares. Orders: A 8,000, B 6,000, C 1,000, D 100 (in that order). Demand 15,100.

1. Guarantee: 100 each → 9,600 left. Remaining demand A 7,900 · B 5,900 · C 900 · D 0.
2. Pro-rata of 9,600: A 5,159 → **5,100**, B 3,853 → **3,800**, C 587 → **500**. 200 left.
3. Leftovers: A (2,800 unfilled) gets 100, then A (2,700) gets 100.

**Final: A 5,400 · B 3,900 · C 600 · D 100** (= 10,000).

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model orders, the book and allocations.
3. Outline the allocation algorithm and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
