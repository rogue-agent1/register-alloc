#!/usr/bin/env python3
"""Register allocation via graph coloring."""

class InterferenceGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def add_var(self, var):
        self.nodes.add(var)

    def add_interference(self, a, b):
        if a != b:
            self.nodes.add(a)
            self.nodes.add(b)
            self.edges.add((min(a,b), max(a,b)))

    def neighbors(self, var):
        n = set()
        for a, b in self.edges:
            if a == var: n.add(b)
            elif b == var: n.add(a)
        return n

    def degree(self, var):
        return len(self.neighbors(var))

def color_graph(graph, num_regs):
    stack = []
    remaining = set(graph.nodes)
    removed_edges = {}
    while remaining:
        low = [v for v in remaining if graph.degree(v) < num_regs
               or not graph.neighbors(v).intersection(remaining)]
        if not low:
            low = [max(remaining, key=lambda v: len(graph.neighbors(v).intersection(remaining)))]
        v = low[0]
        removed_edges[v] = graph.neighbors(v).intersection(remaining)
        remaining.remove(v)
        stack.append(v)
    colors = {}
    spilled = set()
    for v in reversed(stack):
        used = {colors[n] for n in graph.neighbors(v) if n in colors}
        available = [r for r in range(num_regs) if r not in used]
        if available:
            colors[v] = available[0]
        else:
            spilled.add(v)
    return colors, spilled

def from_liveness(live_sets):
    g = InterferenceGraph()
    for live in live_sets:
        for a in live:
            g.add_var(a)
            for b in live:
                if a < b:
                    g.add_interference(a, b)
    return g

def test():
    g = InterferenceGraph()
    for v in ["a", "b", "c", "d"]:
        g.add_var(v)
    g.add_interference("a", "b")
    g.add_interference("a", "c")
    g.add_interference("b", "c")
    g.add_interference("c", "d")
    colors, spilled = color_graph(g, 3)
    assert len(spilled) == 0
    for a, b in g.edges:
        if a in colors and b in colors:
            assert colors[a] != colors[b], f"{a}={colors[a]} == {b}={colors[b]}"
    # With spilling
    g2 = InterferenceGraph()
    for v in ["a", "b", "c", "d", "e"]:
        g2.add_var(v)
    for i, a in enumerate(["a","b","c","d","e"]):
        for b in ["a","b","c","d","e"][i+1:]:
            g2.add_interference(a, b)  # complete graph K5
    colors2, spilled2 = color_graph(g2, 3)
    assert len(spilled2) + len(colors2) == 5
    # From liveness
    g3 = from_liveness([{"a","b"}, {"b","c"}, {"a","c"}])
    colors3, _ = color_graph(g3, 3)
    assert len(colors3) == 3
    print("  register_alloc: ALL TESTS PASSED")

if __name__ == "__main__":
    test()
