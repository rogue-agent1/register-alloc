#!/usr/bin/env python3
"""register_alloc - Graph coloring register allocator."""
import argparse
from collections import defaultdict

class InterferenceGraph:
    def __init__(self): self.nodes=set();self.edges=defaultdict(set)
    def add_node(self, n): self.nodes.add(n)
    def add_edge(self, a, b):
        if a!=b: self.edges[a].add(b);self.edges[b].add(a)
    def degree(self, n): return len(self.edges.get(n,set())&self.nodes)
    def remove(self, n):
        self.nodes.discard(n)
        for nb in self.edges.get(n,set()): self.edges[nb].discard(n)
    def neighbors(self, n): return self.edges.get(n,set())&self.nodes

def build_interference(live_ranges):
    g=InterferenceGraph()
    for var,rng in live_ranges.items(): g.add_node(var)
    vars_list=list(live_ranges.keys())
    for i in range(len(vars_list)):
        for j in range(i+1,len(vars_list)):
            a,b=vars_list[i],vars_list[j]
            ra,rb=live_ranges[a],live_ranges[b]
            if ra[0]<=rb[1] and rb[0]<=ra[1]: g.add_edge(a,b)
    return g

def color_graph(graph, k):
    """Chaitin-style graph coloring with simplification and spilling."""
    allocation={};spilled=set()
    stack=[];nodes=set(graph.nodes)
    remaining=InterferenceGraph()
    remaining.nodes=set(nodes)
    remaining.edges=defaultdict(set)
    for n in nodes:
        for nb in graph.edges.get(n,set()):
            if nb in nodes: remaining.edges[n].add(nb)
    while remaining.nodes:
        simplified=False
        for n in list(remaining.nodes):
            if remaining.degree(n)<k:
                stack.append((n,set(remaining.neighbors(n))))
                remaining.remove(n);simplified=True;break
        if not simplified:
            spill=max(remaining.nodes,key=lambda n:remaining.degree(n))
            spilled.add(spill);remaining.remove(spill)
    while stack:
        n,neighbors=stack.pop()
        used={allocation[nb] for nb in neighbors if nb in allocation}
        for c in range(k):
            if c not in used: allocation[n]=c;break
        else: spilled.add(n)
    return allocation, spilled

def main():
    p=argparse.ArgumentParser(description="Register allocator")
    p.add_argument("-k","--registers",type=int,default=3)
    args=p.parse_args()
    live_ranges={"a":(0,5),"b":(1,8),"c":(3,6),"d":(5,10),"e":(7,12),"f":(0,3),"g":(9,12),"h":(2,4)}
    graph=build_interference(live_ranges)
    print(f"Interference graph: {len(graph.nodes)} vars")
    for n in sorted(graph.nodes):
        nbs=sorted(graph.edges.get(n,set()))
        print(f"  {n}: interferes with {nbs}")
    alloc,spilled=color_graph(graph,args.k)
    reg_names=[f"R{i}" for i in range(args.k)]
    print(f"\nAllocation ({args.k} registers):")
    for v in sorted(alloc): print(f"  {v} -> {reg_names[alloc[v]]}")
    if spilled: print(f"  Spilled: {sorted(spilled)}")

if __name__=="__main__":
    main()
