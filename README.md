# Inspyre‑Vigilance

Real-time system intelligence and event correlation framework.

## Running

Install dependencies with Poetry and launch the default power detector from the Poetry environment:

```bash
poetry install
poetry run python -m inspyre_vigilance
```

## Usage Examples

### Translate power events into display intents

Hook the `PowerDisplayAdapter` into the event bus to convert power events into
semantic display intents without touching LED rendering:

```python
from inspyre_vigilance.core.event_bus import EventBus
from inspyre_vigilance.detectors import PowerDetector
from inspyre_vigilance.outputs.power_display_adapter import PowerDisplayAdapter


def handle_intent(intent):
    print(f"Intent: {intent.category} {intent.severity} {intent.mode} {intent.payload}")


bus = EventBus()
detector = PowerDetector()
adapter = PowerDisplayAdapter(emit_intent=handle_intent)

bus.subscribe(adapter.handle_event)
detector.attach_bus(bus)

detector.dispatch()
```

### Prioritize critical power alerts

The adapter suppresses warning/info intents while a critical alert is active and
resumes normal output after recovery or AC reconnection:

```python
from inspyre_vigilance.events.power import (
    BatteryCritical,
    BatteryRecovered,
    PowerACConnected,
    PowerSource,
    PowerState,
)
from inspyre_vigilance.outputs.power_display_adapter import PowerDisplayAdapter


intents = []
adapter = PowerDisplayAdapter(intents.append)

critical_state = PowerState(False, 5, 120, False, PowerSource.BATTERY)
adapter.handle_event(BatteryCritical(source="demo", state=critical_state))

# Warning/info events would be suppressed here.

recovered_state = PowerState(True, 40, None, True, PowerSource.AC)
adapter.handle_event(PowerACConnected(source="demo", state=recovered_state))
adapter.handle_event(BatteryRecovered(source="demo", state=recovered_state))
```

## Versioning & Changelog

- The source of truth for the version is `[project].version` in `pyproject.toml`.
- For user-facing changes, update `CHANGELOG.md` under **[Unreleased]**.
- Use patch bumps for fixes, minor for features, and major for breaking changes.
- Pre-releases should use a PEP 440 dev suffix (for example, `0.3.0.dev1`).

## Release Workflow

See [.github/workflows/README.md](.github/workflows/README.md) for release triggers,
pre-release detection, required secrets, and publishing behavior.
