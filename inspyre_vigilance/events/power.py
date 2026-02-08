from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from inspyre_vigilance.events.base import Event


class PowerSource(Enum):
    AC = "ac"
    BATTERY = "battery"
    UPS = "ups"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PowerState:
    ac_connected: bool
    battery_percent: Optional[int]
    seconds_remaining: Optional[int]
    charging: Optional[bool]
    source: PowerSource

    def to_payload(self) -> dict:
        return {
            "ac_connected": self.ac_connected,
            "battery_percent": self.battery_percent,
            "seconds_remaining": self.seconds_remaining,
            "charging": self.charging,
            "source": self.source.value,
        }


@dataclass(frozen=True)
class PowerEvent(Event):
    state: Optional[PowerState] = None
    previous_state: Optional[PowerState] = None

    def __post_init__(self):
        if self.state is None:
            raise ValueError("PowerEvent requires a PowerState")

        if not self.payload:
            object.__setattr__(
                self,
                "payload",
                {
                    "state": self.state.to_payload(),
                    "previous_state": self.previous_state.to_payload()
                    if self.previous_state
                    else None,
                },
            )


@dataclass(frozen=True)
class PowerACConnected(PowerEvent):
    name: str = field(init=False, default="PowerACConnected")


@dataclass(frozen=True)
class PowerACDisconnected(PowerEvent):
    name: str = field(init=False, default="PowerACDisconnected")


@dataclass(frozen=True)
class BatteryLevelCrossed(PowerEvent):
    threshold: int = 0
    name: str = field(init=False, default="BatteryLevelCrossed")

    def __post_init__(self):
        super().__post_init__()
        new_payload = dict(self.payload)
        new_payload["threshold"] = self.threshold
        object.__setattr__(self, "payload", new_payload)


@dataclass(frozen=True)
class BatteryCritical(PowerEvent):
    name: str = field(init=False, default="BatteryCritical")


@dataclass(frozen=True)
class BatteryRecovered(PowerEvent):
    name: str = field(init=False, default="BatteryRecovered")


@dataclass(frozen=True)
class ChargingStateChanged(PowerEvent):
    name: str = field(init=False, default="ChargingStateChanged")
