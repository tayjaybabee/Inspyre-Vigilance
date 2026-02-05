class EventBus:
    def __init__(self):
        self._subs = []

    def subscribe(self, handler):
        self._subs.append(handler)

    def publish(self, event):
        for sub in self._subs:
            sub(event)
