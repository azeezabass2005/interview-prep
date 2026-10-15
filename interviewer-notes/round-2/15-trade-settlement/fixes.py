FIXES = [
    ("settle/services/settlement_dates.py",
     "    return calendar.roll_forward(trade.trade_date + timedelta(days=days))",
     "    return calendar.add_business_days(trade.trade_date, days)"),
    ("settle/services/recon.py", "from typing import Dict, List",
     "from decimal import Decimal, InvalidOperation\nfrom typing import Dict, List\n\nfrom ..config import PRICE_TOLERANCE"),
    ("settle/services/recon.py", "        elif float(c.price) != float(trade.price):",
     "        elif abs(Decimal(c.price) - trade.price) > PRICE_TOLERANCE:"),
    ("settle/services/netting.py", "        groups[(t.account, t.security)].append(t)",
     "        groups[(t.account, t.security, settlement_date(t, calendar))].append(t)"),
    ("settle/db.py",
     "CREATE TABLE IF NOT EXISTS instruction_trades (\n    instruction_id  INTEGER NOT NULL,\n    trade_id        TEXT NOT NULL\n);",
     "CREATE TABLE IF NOT EXISTS instruction_trades (\n    instruction_id  INTEGER NOT NULL,\n    trade_id        TEXT NOT NULL UNIQUE\n);"),
    ("settle/services/instructions.py",
     """        created = 0
        for (account, security), group in sorted(netting_groups(self._trades.all(), self._calendar).items()):""",
     """        created = 0
        done = self._instructions.instructed_trade_ids()
        pending = [t for t in self._trades.all() if t.trade_id not in done]
        for (account, security, _), group in sorted(netting_groups(pending, self._calendar).items()):"""),
]
