from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Set


@dataclass(frozen=True)
class Assignment:
    assignment_id: str
    category: str
    max_points: Decimal
    due: datetime


@dataclass
class Submission:
    student: str
    assignment_id: str
    submitted_at: datetime
    points: Optional[Decimal] = None


@dataclass
class Course:
    course_id: str
    assignments: Dict[str, Assignment] = field(default_factory=dict)
    students: Set[str] = field(default_factory=set)
    submissions: Dict[tuple, Submission] = field(default_factory=dict)
    excused: Set[tuple] = field(default_factory=set)
