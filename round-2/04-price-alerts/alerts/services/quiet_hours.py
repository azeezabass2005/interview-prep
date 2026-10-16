from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from ..models import User


def _parse(hhmm: str) -> time:
    hours, minutes = hhmm.split(":")
    return time(int(hours), int(minutes))


def in_quiet_hours(user: User, utc_now: datetime) -> bool:
    local = utc_now.astimezone(ZoneInfo(user.timezone)).time()
    start, end = _parse(user.quiet_start), _parse(user.quiet_end)
    return start <= local < end


def deliver_after(user: User, utc_now: datetime) -> datetime:
    if not in_quiet_hours(user, utc_now):
        return utc_now
    tz = ZoneInfo(user.timezone)
    local = utc_now.astimezone(tz)
    end = _parse(user.quiet_end)
    release = local.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
    if release <= local:
        release += timedelta(days=1)
    return release.astimezone(utc_now.tzinfo)
