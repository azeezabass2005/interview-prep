FIXES = [
    ("drip/processor.py", "holdings = self._ledger.positions()", "holdings = self._ledger.positions_as_of(event.record_date)"),
    ("drip/processor.py",
     """        fee = min(REINVEST_FEE, (gross * FEE_CAP_RATE).quantize(CENT, rounding=ROUND_HALF_UP))
        withholding = self._withholding(account, gross - fee)
        investable = gross - withholding - fee
        shares = (investable / event.reinvest_price).quantize(SHARE_UNIT, rounding=ROUND_HALF_UP)""",
     """        withholding = self._withholding(account, gross)
        net = gross - withholding
        fee = min(REINVEST_FEE, (net * FEE_CAP_RATE).quantize(CENT, rounding=ROUND_HALF_UP))
        investable = net - fee + self.residual_for(account.account_id)
        shares = (investable / event.reinvest_price).quantize(SHARE_UNIT, rounding=ROUND_DOWN)"""),
]
