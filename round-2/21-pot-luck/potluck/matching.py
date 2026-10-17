from collections import Counter


def match_count(entry_code: str, winning_code: str) -> int:
    common = Counter(entry_code) & Counter(winning_code)
    return sum(common.values())


def group_by_matches(entries, winning_code: str):
    groups = {}
    for entry in entries:
        matches = match_count(entry.code, winning_code)
        groups.setdefault(matches, []).append(entry)
    return groups
