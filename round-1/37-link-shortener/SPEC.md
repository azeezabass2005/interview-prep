# Link Shortener

An internal URL shortener turns long links into short codes like `go/Ab3x9Z`. `shortener.py` creates, resolves and deletes links.

## Creating links

- The long URL must start with `http://` or `https://`.
- **Generated codes:** each new link gets the next number from a counter (starting at 1), written in **base 62** using the alphabet
  `0-9`, `a-z`, `A-Z` (most significant digit first) and left-padded with `0` to at least **6** characters. So 1 → `000001`,
  62 → `000010`.
- **Custom aliases** (optional): 3–20 characters from `a-z`, `0-9` and `-`, **case-insensitive** (`Promo` and `promo` are the same alias),
  unique, and not one of the reserved words `admin`, `api`, `login`.
- If the **same user** shortens the same long URL again (without an alias), they get their **existing** link back. Different users always get
  their own links.
- Links may have an expiry time.

## Resolving

`resolve(code)` returns 301 and the URL, and counts a click. Unknown codes → 404. A link is expired **from** its expiry time onward → 410.
Aliases resolve case-insensitively.

## Deleting

Only the owner can delete a link; deleted links → 404.

## Other operations

- `links_of(owner)`: a user's live links, by code.
- `extend(code, user, new_expiry)`: the owner can change or remove (`None`) the expiry; a new expiry must be in the future.
- `top(n)`: the most-clicked live links (ties by code).

## Example

Ana shortens `https://example.com/q3-report` → `000001`. Ana shortens it again → `000001` again.
