"""Host-side anti-cheat: sanity checks on client messages.

No cryptography here — this catches accidents and casual cheating:
teleports, impossible damage claims, and message floods. Three
strikes from one peer and the host kicks it.
"""
import time
from collections import deque

MAX_HIT_CLAIM = 120  # more damage than any legit single hit
MAX_MSG_PER_SEC = 30
MAX_CELL_JUMP = 2  # Manhattan cells between position updates
MAX_WARNS = 3


class HostGuard:
    def __init__(self):
        self.last_pos = {}
        self.msg_times = {}
        self.warns = {}

    def _warn(self, pid, reason):
        self.warns[pid] = self.warns.get(pid, 0) + 1
        return self.warns[pid] >= MAX_WARNS, reason

    def check_rate(self, pid):
        now = time.time()
        times = self.msg_times.setdefault(pid, deque(maxlen=MAX_MSG_PER_SEC + 5))
        times.append(now)
        if len(times) > MAX_MSG_PER_SEC and now - times[0] < 1.0:
            return self._warn(pid, "flood")
        return False, ""

    def check_pos(self, pid, x, y):
        if not (0 <= x < 4 and 0 <= y < 4):
            return self._warn(pid, "out of bounds")
        last = self.last_pos.get(pid)
        self.last_pos[pid] = (x, y)
        if last is not None:
            dx = abs(x - last[0]) + abs(y - last[1])
            if dx > MAX_CELL_JUMP:
                return self._warn(pid, "teleport")
        return False, ""

    def check_boss_hp(self, pid, claimed_drop):
        if claimed_drop > MAX_HIT_CLAIM:
            return self._warn(pid, "impossible damage")
        return False, ""

    def forget(self, pid):
        self.last_pos.pop(pid, None)
        self.msg_times.pop(pid, None)
        self.warns.pop(pid, None)
