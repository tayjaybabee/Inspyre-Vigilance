import time

from inspyre_vigilance.detectors import PowerDetector
from inspyre_vigilance.outputs import PowerDisplayAdapter, StdoutOutput

from .event_bus import EventBus


class VigilanceCore:
    '''Orchestrates detectors and outputs.'''

    def __init__(self, detectors=None, outputs=None, tick_interval: float = 1.0):
        '''Initialize the core, copying detector and output iterables into internal lists.'''
        self.bus = EventBus()
        self.detectors = [] if detectors is None else list(detectors)
        self.outputs = [] if outputs is None else list(outputs)
        if tick_interval <= 0:
            raise ValueError('tick_interval must be positive')
        self.tick_interval = tick_interval
        self._running = False

    def start(self):
        for output in self.outputs:
            self.bus.subscribe(output.handle_event)

        for detector in self.detectors:
            detector.attach_bus(self.bus)

        self._running = True

    def tick(self):
        for detector in self.detectors:
            detector.dispatch()

    def run(self, max_cycles: int | None = None):
        '''Run the detection loop; max_cycles limits ticks, None runs until stop() or a KeyboardInterrupt.'''
        if max_cycles is not None and max_cycles <= 0:
            raise ValueError('max_cycles must be positive when provided')

        self.start()
        cycles = 0

        try:
            while self._running:
                self.tick()
                cycles += 1

                if max_cycles is not None and cycles >= max_cycles:
                    break

                time.sleep(self.tick_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        self._running = False


def main():
    '''Entry point that wires the power detector to stdout output.'''
    power_detector = PowerDetector()
    stdout_output = StdoutOutput()
    display_adapter = PowerDisplayAdapter()
    core = VigilanceCore(detectors=[power_detector], outputs=[stdout_output, display_adapter])
    core.run()
