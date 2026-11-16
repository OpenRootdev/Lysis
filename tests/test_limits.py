from lysis.limits import SlidingWindow, TTLCache


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_sliding_window_blocks_then_recovers():
    clock = Clock()
    w = SlidingWindow(2, window=10, clock=clock)
    assert w.allow("a") and w.allow("a")
    assert not w.allow("a")
    assert w.allow("b")
    clock.t = 11
    assert w.allow("a")


def test_ttl_cache_expires():
    clock = Clock()
    c = TTLCache(ttl=5, clock=clock)
    c.set("k", 1)
    assert c.get("k") == 1
    clock.t = 6
    assert c.get("k") is None