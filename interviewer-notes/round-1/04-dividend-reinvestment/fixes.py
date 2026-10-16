FIXES = [
    ("drip/services/processor.py", "holdings = self._register.holdings(event.security, event.pay_date)",
     "holdings = self._register.holdings(event.security, event.record_date)"),
    ("drip/services/processor.py", "if self._enrolment.currently_enrolled(account_id, event.security):",
     "if self._enrolment.enrolled_on(account_id, event.security, event.record_date):"),
    ("drip/services/processor.py",
     "        fee = min(REINVEST_FEE, (gross * FEE_CAP_RATE).quantize(CENT, rounding=ROUND_HALF_UP))\n        investable = net - fee\n",
     "        fee = min(REINVEST_FEE, (net * FEE_CAP_RATE).quantize(CENT, rounding=ROUND_HALF_UP))\n"
     "        investable = net - fee + self._store.leftover(account.account_id, event.security)\n"),
    ("drip/services/withholding.py", "    return WITHHOLDING_RATES.get(account.country.upper(), Decimal(\"0\"))",
     "    return WITHHOLDING_RATES.get(account.country.upper(), DEFAULT_WITHHOLDING_RATE)"),
]
