from inspyre_vigilance.events.base import Event


class StdoutOutput:
    '''Simple output handler that prints events to stdout.'''

    def handle_event(self, event: Event):
        print(f'[{event.source}] {event.name} -> {event.payload}', flush=True)
