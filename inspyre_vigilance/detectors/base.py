from __future__ import annotations

import time
from typing import Iterable, Optional

from inspyre_vigilance.events.base import Event


class Detector:
    '''Base class for polling detectors.'''

    def __init__(self, name: str, poll_interval: float = 1.0):
        self.name = name
        self.poll_interval = poll_interval
        self._bus = None
        self._last_polled = 0.0

    def attach_bus(self, bus):
        '''Attach the shared event bus.'''
        self._bus = bus

    def ready(self) -> bool:
        '''Determine whether the detector should poll based on interval.'''
        return (time.monotonic() - self._last_polled) >= self.poll_interval

    def poll(self) -> Optional[Iterable[Event]]:
        '''Implement polling logic in subclasses.'''
        raise NotImplementedError

    def dispatch(self):
        '''Poll when ready and publish any resulting events.'''
        if not self.ready():
            return

        self._last_polled = time.monotonic()
        events = self.poll()

        if events is None:
            return

        if not isinstance(events, (list, tuple)):
            events = [events]

        for event in events:
            if self._bus is None:
                continue
            self._bus.publish(event)
