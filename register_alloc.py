#!/usr/bin/env python3
"""Graph coloring register allocator."""
import sys
def build_interference(live_ranges):
    graph={v:set() for v in live_ranges}
    vars=list(live_ranges.keys())
    for i in range(len(vars)):
        for j in range(i+1,len(vars)):
            a,b=vars[i],vars[j]
            s1,e1=live_ranges[a]; s2,e2=live_ranges[b]
            if not(e1<s2 or e2<s1): graph[a].add(b); graph[b].add(a)
    return graph
def color_graph(graph,num_regs):
    order=[]; g={v:set(ns) for v,ns in graph.items()}
    while g:
        v=min(g,key=lambda v:len(g[v])); order.append(v)
        for n in g[v]: g[n].discard(v)
        del g[v]
    colors={}
    for v in reversed(order):
        used={colors[n] for n in graph[v] if n in colors}
        for c in range(num_regs):
            if c not in used: colors[v]=c; break
        else: colors[v]=-1  # spill
    return colors
live_ranges={'a':(0,5),'b':(1,3),'c':(2,6),'d':(4,7),'e':(5,8),'f':(7,9)}
graph=build_interference(live_ranges)
regs=['R0','R1','R2']
colors=color_graph(graph,len(regs))
print("Register allocation (3 registers):")
for v in sorted(colors):
    r=regs[colors[v]] if colors[v]>=0 else 'SPILL'
    print(f"  {v} [{live_ranges[v][0]}-{live_ranges[v][1]}] → {r}")
print(f"\nInterference edges: {sum(len(v) for v in graph.values())//2}")
