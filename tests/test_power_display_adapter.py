from inspyre_vigilance.events.power import BatteryCritical, PowerACConnected, PowerSource, PowerState
from inspyre_vigilance.outputs.display_intent import DisplayMode, Severity
from inspyre_vigilance.outputs.power_display_adapter import PowerDisplayAdapter


def test_power_display_adapter_translates_and_debounces():
    emitted = []
    adapter = PowerDisplayAdapter(emitted.append)

    connected = PowerACConnected(
        source="test",
        state=PowerState(True, 90, None, True, PowerSource.AC),
    )
    adapter.handle_event(connected)
    assert len(emitted) == 1
    assert emitted[0].severity == Severity.INFO
    assert emitted[0].mode == DisplayMode.STEADY
    assert emitted[0].payload["event"] == "PowerACConnected"

    critical_event = BatteryCritical(
        source="test",
        state=PowerState(False, 5, 100, False, PowerSource.BATTERY),
        previous_state=connected.state,
    )
    adapter.handle_event(critical_event)
    assert len(emitted) == 2
    assert emitted[-1].severity == Severity.CRITICAL
    assert emitted[-1].mode == DisplayMode.BLINK

    adapter.handle_event(critical_event)
    assert len(emitted) == 2  # deduped
