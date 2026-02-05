from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    name: str
    source: str
    payload: dict
    confidence: float = 1.0
