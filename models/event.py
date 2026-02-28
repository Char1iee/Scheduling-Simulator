"""Event types for discrete-event simulation."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

from .job import Job


class EventType(Enum):
    ARRIVAL = "arrival"
    COMPLETE = "complete"
    QUANTUM_EXPIRE = "quantum_expire"


@dataclass(order=True)
class Event:
    """A simulation event with timestamp ordering."""

    time: int
    event_type: EventType = field(compare=False)
    job: Optional[Job] = field(compare=False, default=None)
