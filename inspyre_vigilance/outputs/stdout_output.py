from inspyre_vigilance.events.base import Event


class StdoutOutput:
    '''Simple output surface that prints events.'''

    def handle_event(self, event: Event):
        print(f'[{event.source}] {event.name} -> {event.payload}', flush=True)
