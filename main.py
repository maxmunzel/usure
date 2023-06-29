from typing import NamedTuple


class State(NamedTuple):
    time: int = 1

    def next(self):
        yield self._replace(time=(self.time + 1) % 12)

    def safety(self):
        return 0 <= self.time < 12


def check(s: State):
    states = frozenset({s})
    parent = {s: None}

    def trace(s):
        nonlocal parent
        print("Illegal State found!")
        while s is not None:
            print(s)
            s = parent[s]

    def expand(s):
        nonlocal states
        for n in s.next():
            if n in states:
                continue
            parent[n] = s
            if not n.safety():
                trace(n)
                return
            states |= {n}
            expand(n)

    expand(s)


print(check(State()))
