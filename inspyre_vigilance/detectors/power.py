from __future__ import annotations

import psutil

from inspyre_vigilance.events.power import (
    BatteryCritical,
    BatteryLevelCrossed,
    BatteryRecovered,
    ChargingStateChanged,
    PowerACConnected,
    PowerACDisconnected,
    PowerEvent,
    PowerSource,
    PowerState,
)
from .base import Detector


class PowerDetector(Detector):
    '''Detects AC/battery power transitions and emits semantic power events.'''

    def __init__(
        self,
        poll_interval: float = 2.0,
        thresholds: tuple[int, ...] = (20, 10, 5),
        critical_threshold: int = 10,
        recover_threshold: int = 15,
    ):
        super().__init__('PowerDetector', poll_interval=poll_interval)
        self._last_state: PowerState | None = None
        self.thresholds = tuple(sorted(set(thresholds), reverse=True))
        self.critical_threshold = critical_threshold
        self.recover_threshold = recover_threshold

    def read_battery(self):
        '''Thin wrapper around psutil for easier testing.'''
        return psutil.sensors_battery()

    def normalize(self, battery) -> PowerState | None:
        '''Normalize raw psutil battery data into a PowerState snapshot.'''
        if battery is None:
            return None

        ac_connected = bool(getattr(battery, 'power_plugged', False))

        raw_percent = getattr(battery, 'percent', None)
        battery_percent = None
        if raw_percent is not None:
            try:
                percent_int = int(raw_percent)
            except (TypeError, ValueError):
                percent_int = None

            if percent_int is not None and 0 <= percent_int <= 100:
                battery_percent = percent_int

        raw_secs = getattr(battery, 'secsleft', None)
        seconds_remaining = raw_secs
        if raw_secs in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
            seconds_remaining = None
        elif isinstance(raw_secs, (int, float)) and raw_secs < 0:
            seconds_remaining = None

        if battery_percent is None and not ac_connected:
            source = PowerSource.UNKNOWN
        else:
            source = PowerSource.AC if ac_connected else PowerSource.BATTERY

        charging = None
        if battery_percent is not None:
            if ac_connected and battery_percent < 100:
                charging = True
            elif not ac_connected:
                charging = False

        return PowerState(
            ac_connected=ac_connected,
            battery_percent=battery_percent,
            seconds_remaining=seconds_remaining,
            charging=charging,
            source=source,
        )

    def diff(self, new_state: PowerState) -> list[PowerEvent]:
        '''Compare the new state against the last snapshot and emit transitions.'''
        events: list[PowerEvent] = []

        if self._last_state is None:
            self._last_state = new_state
            return events

        prev = self._last_state

        if new_state.ac_connected != prev.ac_connected:
            if new_state.ac_connected:
                events.append(PowerACConnected(source=self.name, state=new_state, previous_state=prev))
            else:
                events.append(PowerACDisconnected(source=self.name, state=new_state, previous_state=prev))

        if new_state.charging != prev.charging:
            events.append(ChargingStateChanged(source=self.name, state=new_state, previous_state=prev))

        if (
            not new_state.ac_connected
            and new_state.battery_percent is not None
            and prev.battery_percent is not None
        ):
            for threshold in self.thresholds:
                if new_state.battery_percent <= threshold < prev.battery_percent:
                    events.append(
                        BatteryLevelCrossed(
                            source=self.name,
                            state=new_state,
                            previous_state=prev,
                            threshold=threshold,
                        )
                    )

        if (
            not new_state.ac_connected
            and new_state.battery_percent is not None
            and new_state.battery_percent <= self.critical_threshold
            and (prev.battery_percent is None or prev.battery_percent > self.critical_threshold)
        ):
            events.append(BatteryCritical(source=self.name, state=new_state, previous_state=prev))

        if (
            prev.battery_percent is not None
            and prev.battery_percent <= self.critical_threshold
            and new_state.battery_percent is not None
            and new_state.battery_percent >= self.recover_threshold
        ):
            events.append(BatteryRecovered(source=self.name, state=new_state, previous_state=prev))

        self._last_state = new_state
        return events

    def poll(self):
        battery = self.read_battery()
        state = self.normalize(battery)

        if state is None:
            return None

        events = self.diff(state)
        return events if events else None
