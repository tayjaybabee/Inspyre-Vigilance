import psutil

from inspyre_vigilance.detectors.power import PowerDetector
from inspyre_vigilance.events.power import (
    BatteryCritical,
    BatteryLevelCrossed,
    BatteryRecovered,
    ChargingStateChanged,
    PowerACConnected,
    PowerACDisconnected,
    PowerSource,
    PowerState,
)


class FakeBattery:
    def __init__(self, percent, power_plugged, secsleft):
        self.percent = percent
        self.power_plugged = power_plugged
        self.secsleft = secsleft


def test_normalize_sanitizes_battery_snapshot():
    detector = PowerDetector()

    battery = FakeBattery(50.7, True, psutil.POWER_TIME_UNKNOWN)
    normalized = detector.normalize(battery)

    assert normalized.ac_connected is True
    assert normalized.battery_percent == 50
    assert normalized.seconds_remaining is None
    assert normalized.charging is True
    assert normalized.source == PowerSource.AC

    battery = FakeBattery(150, False, -1)
    normalized = detector.normalize(battery)
    assert normalized.battery_percent is None
    assert normalized.seconds_remaining is None
    assert normalized.source == PowerSource.UNKNOWN


def test_power_detector_emits_transitions():
    detector = PowerDetector(thresholds=(25, 10), critical_threshold=10, recover_threshold=15)

    baseline = PowerState(True, 80, 1000, True, PowerSource.AC)
    assert detector.diff(baseline) == []

    disconnected = PowerState(False, 80, 900, False, PowerSource.BATTERY)
    events = detector.diff(disconnected)
    assert any(isinstance(e, PowerACDisconnected) for e in events)
    assert any(isinstance(e, ChargingStateChanged) for e in events)

    crossed = PowerState(False, 24, 800, False, PowerSource.BATTERY)
    events = detector.diff(crossed)
    assert any(isinstance(e, BatteryLevelCrossed) and e.threshold == 25 for e in events)

    critical = PowerState(False, 9, 700, False, PowerSource.BATTERY)
    events = detector.diff(critical)
    assert any(isinstance(e, BatteryLevelCrossed) and e.threshold == 10 for e in events)
    assert any(isinstance(e, BatteryCritical) for e in events)

    recovered = PowerState(True, 50, psutil.POWER_TIME_UNLIMITED, True, PowerSource.AC)
    events = detector.diff(recovered)
    assert any(isinstance(e, PowerACConnected) for e in events)
    assert any(isinstance(e, ChargingStateChanged) for e in events)
    assert any(isinstance(e, BatteryRecovered) for e in events)
