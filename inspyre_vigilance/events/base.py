import time
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Event:
    name: str
    source: str
    payload: dict = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
