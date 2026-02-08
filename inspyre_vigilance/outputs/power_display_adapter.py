from __future__ import annotations

from typing import Callable, Iterable

from inspyre_vigilance.events.power import (
    BatteryCritical,
    BatteryLevelCrossed,
    BatteryRecovered,
    PowerACConnected,
    PowerACDisconnected,
    PowerEvent,
)

from .display_intent import DisplayIntent, DisplayMode, Severity


class PowerDisplayAdapter:
    '''Translates power events into display intents without rendering pixels.'''

    def __init__(self, emit_intent: Callable[[DisplayIntent], None] | None = None):
        self.emit_intent = emit_intent or (lambda intent: print(intent, flush=True))
        self._last_intent: DisplayIntent | None = None

    def _emit_if_new(self, intent: DisplayIntent):
        if self._last_intent == intent:
            return
        self._last_intent = intent
        self.emit_intent(intent)

    def handle_event(self, event):
        intents = list(self.translate(event))
        for intent in intents:
            self._emit_if_new(intent)

    def translate(self, event) -> Iterable[DisplayIntent]:
        if not isinstance(event, PowerEvent):
            return []

        payload = dict(event.state.to_payload())
        payload["event"] = event.name

        if isinstance(event, PowerACConnected):
            return [
                DisplayIntent(
                    category="power",
                    severity=Severity.INFO,
                    mode=DisplayMode.STEADY,
                    payload=payload,
                )
            ]

        if isinstance(event, PowerACDisconnected):
            return [
                DisplayIntent(
                    category="power",
                    severity=Severity.WARNING,
                    mode=DisplayMode.PULSE,
                    payload=payload,
                )
            ]

        if isinstance(event, BatteryCritical):
            return [
                DisplayIntent(
                    category="power",
                    severity=Severity.CRITICAL,
                    mode=DisplayMode.BLINK,
                    payload=payload,
                )
            ]

        if isinstance(event, BatteryRecovered):
            return [
                DisplayIntent(
                    category="power",
                    severity=Severity.INFO,
                    mode=DisplayMode.STEADY,
                    payload=payload,
                )
            ]

        if isinstance(event, BatteryLevelCrossed):
            payload = dict(payload)
            payload["threshold"] = event.threshold
            return [
                DisplayIntent(
                    category="power",
                    severity=Severity.WARNING,
                    mode=DisplayMode.PULSE,
                    payload=payload,
                )
            ]

        return [
            DisplayIntent(
                category="power",
                severity=Severity.INFO,
                mode=DisplayMode.STEADY,
                payload=payload,
            )
        ]
