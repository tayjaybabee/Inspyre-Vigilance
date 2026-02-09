from inspyre_vigilance.events.power import (
    BatteryCritical,
    BatteryLevelCrossed,
    PowerACConnected,
    PowerACDisconnected,
    PowerSource,
    PowerState,
)
from inspyre_vigilance.outputs.display_intent import DisplayMode, Severity
from inspyre_vigilance.outputs.power_display_adapter import PowerDisplayAdapter


def test_power_display_adapter_translates_and_debounces():
    emitted = []
    adapter = PowerDisplayAdapter(emitted.append)

    connected_state = PowerState(True, 90, None, True, PowerSource.AC)
    connected = PowerACConnected(source="test", state=connected_state)
    adapter.handle_event(connected)
    assert len(emitted) == 1
    assert emitted[0].severity == Severity.INFO
    assert emitted[0].mode == DisplayMode.STEADY
    assert emitted[0].payload["event"] == "PowerACConnected"

    disconnected_state = PowerState(False, 30, None, False, PowerSource.BATTERY)
    disconnected = PowerACDisconnected(
        source="test",
        state=disconnected_state,
        previous_state=connected_state,
    )
    adapter.handle_event(disconnected)
    assert len(emitted) == 2
    assert emitted[-1].severity == Severity.WARNING

    critical_event = BatteryCritical(
        source="test",
        state=PowerState(False, 5, 100, False, PowerSource.BATTERY),
        previous_state=connected.state,
    )
    adapter.handle_event(critical_event)
    assert len(emitted) == 3
    assert emitted[-1].severity == Severity.CRITICAL
    assert emitted[-1].mode == DisplayMode.BLINK

    crossed_event = BatteryLevelCrossed(
        source="test",
        state=PowerState(False, 4, 90, False, PowerSource.BATTERY),
        previous_state=critical_event.state,
        threshold=10,
    )
    adapter.handle_event(crossed_event)
    assert len(emitted) == 3  # suppressed by critical priority

    adapter.handle_event(critical_event)
    assert len(emitted) == 3  # deduped

    adapter.handle_event(connected)
    assert len(emitted) == 4
    assert emitted[-1].severity == Severity.INFO
