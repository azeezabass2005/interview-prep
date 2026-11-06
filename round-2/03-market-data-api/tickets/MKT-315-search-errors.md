# MKT-315: Instrument search fails for some names

**Type:** Bug · **Priority:** High · **Reporter:** Web team, then Security Engineering

## Description
Searching for "O'Reilly" in the web app shows "Internal server error". A security review then found that searching for
`zzz' OR '1'='1` returns the entire instrument table, so the search box can be used to run arbitrary SQL against our
database.

## Acceptance criteria
- Names with quotes, apostrophes or other punctuation can be searched and found (`O'Reilly` finds ORLY).
- User input can't change the meaning of any query.
- Search keeps working as documented (names anywhere, symbols by prefix, case-insensitive).
