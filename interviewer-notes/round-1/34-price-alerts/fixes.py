FIXES = [
    ("alerts.py", "            return price > alert.threshold", "            return price >= alert.threshold"),
    ("alerts.py", "        alert = Alert(alert_id, user, symbol, condition, Decimal(str(threshold)), recurring)\n",
     "        alert = Alert(alert_id, user, symbol, condition, Decimal(str(threshold)), recurring)\n"
     "        last = self.last_price.get(symbol)\n"
     "        alert.armed = last is None or not self._holds(alert, last)\n"),
    ("alerts.py", "                    alert.armed = False", "                    alert.armed = False\n                    alert.active = alert.recurring"),
    ("alerts.py", "        if start <= local.time() < end:",
     "        now = local.time()\n        quiet = start <= now < end if start < end else (now >= start or now < end)\n        if quiet:"),
    ("alerts.py", "if n.created_at.date() == at.date() and n.status",
     "if n.user == alert.user and n.created_at.date() == at.date() and n.status"),
]
