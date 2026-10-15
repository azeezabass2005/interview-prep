from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Dict, List

from .constants import CENT, FEE_CAP_RATE, NON_RESIDENT_WITHHOLDING, REINVEST_FEE, SHARE_UNIT, ZERO
from .ledger import Ledger
from .models import Account, DividendEvent, DividendPayment


class DripProcessor:
    def __init__(self, ledger: Ledger, accounts: Dict[str, Account]):
        self._ledger = ledger
        self._accounts = accounts
        self._residuals: Dict[str, Decimal] = {}

    def residual_for(self, account_id: str) -> Decimal:
        return self._residuals.get(account_id, ZERO)

    def process(self, event: DividendEvent) -> List[DividendPayment]:
        payments = []
        holdings = self._ledger.positions()
        for account_id, shares in sorted(holdings.items()):
            if shares <= 0:
                continue
            account = self._accounts[account_id]
            gross = (shares * event.per_share).quantize(CENT, rounding=ROUND_DOWN)
            if account.drip_enrolled:
                payments.append(self._reinvest(account, gross, event))
            else:
                withholding = self._withholding(account, gross)
                payments.append(DividendPayment(account_id, gross, withholding, ZERO,
                                                gross - withholding, ZERO, ZERO))
        return payments

    def _withholding(self, account: Account, amount: Decimal) -> Decimal:
        if account.resident:
            return ZERO
        return (amount * NON_RESIDENT_WITHHOLDING).quantize(CENT, rounding=ROUND_HALF_UP)

    def _reinvest(self, account: Account, gross: Decimal, event: DividendEvent) -> DividendPayment:
        fee = min(REINVEST_FEE, (gross * FEE_CAP_RATE).quantize(CENT, rounding=ROUND_HALF_UP))
        withholding = self._withholding(account, gross - fee)
        investable = gross - withholding - fee
        shares = (investable / event.reinvest_price).quantize(SHARE_UNIT, rounding=ROUND_HALF_UP)
        residual = investable - shares * event.reinvest_price
        self._residuals[account.account_id] = residual
        self._ledger.record(event.pay_date, account.account_id, shares)
        return DividendPayment(account.account_id, gross, withholding, fee, ZERO, shares, residual)
