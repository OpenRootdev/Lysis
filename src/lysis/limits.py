"""In-memory rate limiting and response cache (single process)."""

import time
from collections import defaultdict, deque


class SlidingWindow:
    def __init__(self, limit, window=3600.0, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.hits = defaultdict(deque)

    def allow(self, key):
        now = self.clock()
        q = self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(self.hits) > 5000:
            for k in [k for k, v in self.hits.items() if not v and k != key]:
                del self.hits[k]
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True


class TTLCache:
    def __init__(self, ttl=600.0, max_items=200, clock=time.monotonic):
        self.ttl, self.max_items, self.clock = ttl, max_items, clock
        self.data = {}

    def get(self, key):
        item = self.data.get(key)
        if item and self.clock() - item[0] < self.ttl:
            return item[1]
        self.data.pop(key, None)
        return None

    def set(self, key, value):
        if len(self.data) >= self.max_items:
            del self.data[min(self.data, key=lambda k: self.data[k][0])]
        self.data[key] = (self.clock(), value)