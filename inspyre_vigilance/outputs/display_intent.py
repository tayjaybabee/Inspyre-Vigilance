from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DisplayMode(str, Enum):
    STEADY = "steady"
    PULSE = "pulse"
    BLINK = "blink"


@dataclass(frozen=True)
class DisplayIntent:
    category: str
    severity: Severity
    mode: DisplayMode
    payload: dict
    timestamp: float = field(default_factory=time.monotonic, compare=False)
