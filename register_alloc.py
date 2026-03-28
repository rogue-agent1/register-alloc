#!/usr/bin/env python3
"""Register allocator (graph coloring)."""
from collections import defaultdict
class InterferenceGraph:
    def __init__(self): self.nodes=set();self.edges=defaultdict(set)
    def add_var(self,v): self.nodes.add(v)
    def add_interference(self,u,v):
        self.nodes.add(u);self.nodes.add(v)
        self.edges[u].add(v);self.edges[v].add(u)
    def degree(self,v): return len(self.edges[v])
def color_graph(graph,num_regs):
    stack=[];nodes=set(graph.nodes);removed=defaultdict(set)
    while nodes:
        low=[v for v in nodes if graph.degree(v)-len(removed[v])<num_regs]
        if low: v=low[0]
        else: v=max(nodes,key=lambda x:graph.degree(x)-len(removed[x]))
        stack.append(v);nodes.remove(v)
        for u in graph.edges[v]: removed[u].add(v)
    colors={};spilled=[]
    while stack:
        v=stack.pop()
        used={colors[u] for u in graph.edges[v] if u in colors}
        for c in range(num_regs):
            if c not in used: colors[v]=c;break
        else: spilled.append(v)
    return colors,spilled
def from_liveness(live_sets):
    g=InterferenceGraph()
    for live in live_sets:
        vs=list(live)
        for i in range(len(vs)):
            g.add_var(vs[i])
            for j in range(i+1,len(vs)):
                g.add_interference(vs[i],vs[j])
    return g
if __name__=="__main__":
    live_sets=[{"a","b"},{"b","c"},{"a","c","d"},{"c","d"}]
    g=from_liveness(live_sets)
    colors,spilled=color_graph(g,3)
    print(f"Allocation (3 regs): {colors}")
    print(f"Spilled: {spilled}")
    assert len(spilled)==0
    colors2,spilled2=color_graph(g,2)
    print(f"Allocation (2 regs): {colors2}, spilled: {spilled2}")
    print("Register allocator OK")
