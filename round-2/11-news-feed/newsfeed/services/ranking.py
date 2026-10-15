from datetime import datetime

from ..config import HALF_LIFE_HOURS
from ..models import Story
from ..sources import weight_for


def score(story: Story, now: datetime) -> float:
    age_hours = (now - story.published_at).total_seconds() / 86400
    return weight_for(story.source) * 0.5 ** (age_hours / HALF_LIFE_HOURS)
