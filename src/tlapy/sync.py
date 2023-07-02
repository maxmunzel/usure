from typing import NamedTuple
import random

N = 3


class State(NamedTuple):
    inflight_limit: int = 3
    open_msgs: tuple[int] = tuple(range(N))
    received_msgs: frozenset[int] = frozenset()
    http_ok: tuple[int] = tuple()
    http_err: tuple[int] = tuple()

    def next(self):
        yield from self.send_message()
        yield from self.handle_err()
        yield from self.handle_ok()

    def send_message(self):
        if len(self.http_ok) + len(self.http_err) < self.inflight_limit and self.open_msgs:
            msg = (self.open_msgs[0],)
            # success
            yield f"suc", self._replace(http_ok=self.http_ok + msg, received_msgs=self.received_msgs | set(msg))
            # failure
            yield "fail", self._replace(http_err=self.http_ok + msg)
        return
        yield

    def handle_err(self):
        for i, err in enumerate(self.http_err):
            new_http_err = tuple(msg for j, msg in enumerate(self.http_err) if i != j)
            yield f"err {err}", self._replace(http_err=new_http_err)
        return
        yield

    def handle_ok(self):
        for i, msg in enumerate(self.http_ok):
            new_http_ok = tuple(msg for j, msg in enumerate(self.http_ok) if i != j)
            if not self.open_msgs or self.open_msgs[0] != msg:
                # ignore if nothing left to send
                new_open_msgs = self.open_msgs
            else:
                # otherwise pop one from queue, iff its the correct one
                new_open_msgs = self.open_msgs[1:]

            yield f"ok {msg}", self._replace(http_ok=new_http_ok, open_msgs=new_open_msgs)
        return
        yield

    def safety(self):
        deadlock = len(list(self.next())) == 0
        if deadlock:
            return False
        if deadlock and self.received_msgs != set(range(N)):
            return False
        if deadlock and len(self.open_msgs) != 0:
            return False
        return True

    def __repr__(self):
        return (
            f"<open: {self.open_msgs} ok: {self.http_ok} fail: {self.http_err} recv: {set(self.received_msgs) or '{}'}>"
        )


def check(s: State):
    states = frozenset({s})
    parent = {s: ("init", None)}

    def trace(s):
        nonlocal parent
        print("Illegal State found!")
        msg = ""
        while s is not None:
            print(msg, "\t", s)
            msg, s = parent[s]

    def expand(s) -> bool:
        nonlocal states
        for msg, n in s.next():
            if n in states:
                continue
            parent[n] = (msg, s)
            if not n.safety():
                trace(n)
                return False
            states |= {n}
            if not expand(n):
                return False
        return True

    expand(s)
    return len(states)


def trace(s: State, max_len=100):
    n = [("init", s)]
    i = 0
    while len(n) != 0 and i < max_len:
        i += 1
        msg, s = random.choice(n)
        print(msg, "\t", s)
        n = list(set(s.next()))


if __name__ == "__main__":
    print(check(State()))
