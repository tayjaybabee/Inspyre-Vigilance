from __future__ import annotations

import psutil

from inspyre_vigilance.events.base import Event
from .base import Detector


class PowerDetector(Detector):
    '''Detects AC power connection changes.'''

    def __init__(self, poll_interval: float = 2.0):
        super().__init__('PowerDetector', poll_interval=poll_interval)
        self._last_connected = None

    def poll(self):
        battery = psutil.sensors_battery()

        if battery is None:
            return None

        ac_connected = bool(battery.power_plugged)

        if self._last_connected is not None and ac_connected == self._last_connected:
            return None

        self._last_connected = ac_connected
        event_name = 'ACConnected' if ac_connected else 'ACDisconnected'
        payload = {
            'ac_connected': ac_connected,
            'percent': battery.percent,
            'secs_left': battery.secsleft,
        }
        return Event(name=event_name, source=self.name, payload=payload)
