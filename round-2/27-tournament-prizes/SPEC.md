# Card Room Tournament Manager

A card room runs weekly freeze-out tournaments with re-entry. The tournament director's software registers players, records
eliminations hand by hand, and pays prizes and bounties at the end. The repository contains that software.

## Registration and re-entry

- Buy-in is **$55** per entry: **$45** goes to the prize pool side, **$10** is the entry's **bounty**.
- Players register before the start or during **late registration**, which stays open **through the end of level 6** (blind levels
  are numbered from 1; the director advances levels manually).
- A busted player may **re-enter** (buy a new entry) during late registration. A player can have **at most 2 re-entries** (3 entries
  in total) and only one live entry at a time.

## Prize pool

- **Rake:** the house keeps **10% of the prize-pool side** of all entries (rounded down to the cent).
- **Guarantee:** the prize pool is at least **$2,000**. If the prize-pool side minus rake is less, the house adds the difference.
- Places paid depend on the number of **entries** (re-entries count):

| Entries | Paid places (% of prize pool) |
|---|---|
| up to 10 | 65 / 35 |
| 11 – 30 | 50 / 30 / 20 |
| 31 or more | 40 / 25 / 15 / 12 / 8 |

- Each place amount is rounded down to the cent; leftover cents go to **1st place**.

## Eliminations and finishing places

- Eliminations are recorded per hand: the hand number, the eliminated player(s), and the player who won the pot.
- A player's finishing place is decided by their **final** elimination (one with no re-entry after it).
- Players eliminated **in the same hand** tie: they share the places they occupy equally, and the next place skips accordingly.
  Leftover cents from a tie split go one each to tied players in alphabetical order.
- The last player standing is 1st.

## Bounties

Every time an entry is eliminated, its **$10 bounty** goes to the player who won that pot (split equally, rounded down, if several
players shared the pot; leftover cents to the first in alphabetical order).

## Examples

- 61 entries → prize side 61 × $45 = $2,745.00; rake $274.50; net $2,470.50 → pool **$2,470.50** (above the guarantee).
- 20 entries → net $810.00 → the guarantee applies: pool **$2,000.00**, paid 50 / 30 / 20.
- 20 entries: ana wins; ben and cy bust in the same hand as 2nd/3rd → each gets (600 + 400) / 2 = **$500**; dee (4th) gets nothing.
