from typing import Dict, List

from ..models import Transfer


def suggest_transfers(balances: Dict[str, int]) -> List[Transfer]:
    debtors = {m: -b for m, b in balances.items() if b < 0}
    creditors = {m: b for m, b in balances.items() if b > 0}
    transfers = []
    while debtors and creditors:
        debtor = sorted(debtors, key=lambda m: (-debtors[m], m))[0]
        creditor = sorted(creditors, key=lambda m: (creditors[m], m))[0]
        amount = min(debtors[debtor], creditors[creditor])
        transfers.append(Transfer(debtor, creditor, amount))
        debtors[debtor] -= amount
        creditors[creditor] -= amount
        if debtors[debtor] == 0:
            del debtors[debtor]
        if creditors[creditor] == 0:
            del creditors[creditor]
    return transfers
