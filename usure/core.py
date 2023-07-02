from typing import Protocol, Iterable
import networkx as nx


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


def check(init: State) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node(init)
    unsafe_states = set()

    def expand(s: State):
        if not s.safety():
            unsafe_states.add(s)
        for msg, n in s.next():
            if n not in graph.nodes:
                expand(n)
            graph.add_edge(s, n)
            graph.edges[s, n]["msg"] = msg

    expand(init)

    if not unsafe_states:
        return graph

    distance_from_init, path_from_init = nx.single_source_dijkstra(graph, init)  # type: ignore
    distance_from_init: dict[State, float]
    path_from_init: dict[State, list[State]]

    shortest_unsafe: State
    shortest_unsafe, _ = min(
        (state, distance_from_init[state]) for state in unsafe_states
    )

    prev: State = init
    print(f"Init\t{init}")
    for state in path_from_init[shortest_unsafe][1:]:
        msg = graph.edges[prev, state]["msg"]
        print(f"{msg}\t{state}")
        prev = state

    return graph


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
