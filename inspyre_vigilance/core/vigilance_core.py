from .event_bus import EventBus

class VigilanceCore:
    def __init__(self, detectors=None, outputs=None):
        self.bus = EventBus()
        self.detectors = detectors or []
        self.outputs = outputs or []

    def start(self):
        for output in self.outputs:
            self.bus.subscribe(output.handle_event)

    def stop(self):
        pass

def main():
    core = VigilanceCore()
    core.start()
