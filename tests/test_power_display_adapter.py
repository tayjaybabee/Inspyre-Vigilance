from inspyre_vigilance.events.power import (
    BatteryCritical,
    BatteryLevelCrossed,
    BatteryRecovered,
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
        state=PowerState(False, 9, 90, False, PowerSource.BATTERY),
        previous_state=PowerState(False, 11, 95, False, PowerSource.BATTERY),
        threshold=10,
    )
    adapter.handle_event(crossed_event)
    assert len(emitted) == 3  # suppressed by critical priority

    adapter.handle_event(critical_event)
    assert len(emitted) == 3  # deduped

    # Test INFO suppression during WARNING
    # Set WARNING as active and verify PowerACConnected (recovery) emits
    adapter._active_severity = Severity.WARNING
    adapter._last_intent = None
    reconnect_state = PowerState(True, 20, None, True, PowerSource.AC)
    info_reconnect = PowerACConnected(source="test", state=reconnect_state)

    initial_count = len(emitted)
    adapter.handle_event(info_reconnect)
    assert len(emitted) == initial_count + 1  # PowerACConnected emits even during WARNING (recovery event)
    assert emitted[-1].severity == Severity.INFO

    # Test BatteryRecovered clears suppression
    adapter._active_severity = Severity.CRITICAL  # Set to CRITICAL
    recovered_state = PowerState(True, 60, None, True, PowerSource.AC)
    recovered_event = BatteryRecovered(
        source="test",
        state=recovered_state,
        previous_state=critical_event.state,
    )
    initial_count = len(emitted)
    adapter.handle_event(recovered_event)
    assert len(emitted) == initial_count + 1  # BatteryRecovered emits and clears suppression
    assert emitted[-1].severity == Severity.INFO
    assert adapter._active_severity == Severity.INFO  # Suppression cleared

    adapter.handle_event(connected)
    assert len(emitted) == initial_count + 2
    assert emitted[-1].severity == Severity.INFO
