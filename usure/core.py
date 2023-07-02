from typing import Protocol, Iterable


class State(Protocol):
    def next(self) -> Iterable[tuple[str, "State"]]:
        """An iterable over all (transition, next_state) tuples from this State."""
        ...

    def safety(self) -> bool:
        """Does this state fulfill all the safety properties?"""
        ...

    def __hash__(self) -> int:
        """All States have to implement meaningful hashes, as they are stored as graph nodes.
        A good strategy is to use immutable members like (named) tuples and frozensets."""
        ...


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
