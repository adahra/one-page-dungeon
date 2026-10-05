"""Tiny publish/subscribe bus to decouple game logic from effects.

Logic emits events (hit/kill/hurt/...); App wires subscribers for
sound, particles, log, and screen shake at startup.
"""
SUBSCRIBERS = {}


class Bus:
    def __init__(self):
        self._subs = {}

    def sub(self, event, fn):
        self._subs.setdefault(event, []).append(fn)
        return fn

    def emit(self, event, **data):
        for fn in self._subs.get(event, []):
            fn(**data)

    def clear(self):
        self._subs.clear()
