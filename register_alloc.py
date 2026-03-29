#!/usr/bin/env python3
"""Register Allocator - Graph coloring register allocation for virtual registers."""
import sys, re
from collections import defaultdict

def parse_instrs(text):
    instrs = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        instrs.append(line)
    return instrs

def get_vars(instrs):
    defs = []; uses = []
    for instr in instrs:
        m = re.match(r"(\w+)\s*=\s*(.*)", instr)
        if m:
            defs.append({m.group(1)})
            uses.append(set(re.findall(r"[a-zA-Z_]\w*", m.group(2))))
        else:
            defs.append(set())
            uses.append(set(re.findall(r"[a-zA-Z_]\w*", instr)) - {"print", "return", "if", "goto"})
    return defs, uses

def liveness(instrs, defs_list, uses_list):
    n = len(instrs)
    live_in = [set() for _ in range(n)]
    live_out = [set() for _ in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n - 1, -1, -1):
            new_out = live_in[i + 1] if i + 1 < n else set()
            new_in = uses_list[i] | (new_out - defs_list[i])
            if new_in != live_in[i] or new_out != live_out[i]:
                live_in[i] = new_in; live_out[i] = new_out; changed = True
    return live_in, live_out

def build_interference(live_out, defs_list):
    graph = defaultdict(set)
    all_vars = set()
    for lo, d in zip(live_out, defs_list):
        all_vars |= lo | d
        for v in d:
            for u in lo:
                if u != v:
                    graph[v].add(u); graph[u].add(v)
    for v in all_vars:
        graph.setdefault(v, set())
    return graph

def color_graph(graph, k):
    nodes = list(graph.keys())
    stack = []; removed = set(); temp_graph = {n: set(s) for n, s in graph.items()}
    while len(removed) < len(nodes):
        found = False
        for n in nodes:
            if n in removed: continue
            degree = len(temp_graph[n] - removed)
            if degree < k:
                stack.append(n); removed.add(n); found = True; break
        if not found:
            for n in nodes:
                if n not in removed:
                    stack.append(n); removed.add(n); break
    colors = {}
    while stack:
        n = stack.pop()
        used = {colors[nb] for nb in graph[n] if nb in colors}
        for c in range(k):
            if c not in used: colors[n] = c; break
        else:
            colors[n] = -1
    return colors

def main():
    if len(sys.argv) < 2:
        print("Usage: register_alloc.py <file> [num-registers]"); sys.exit(1)
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with open(sys.argv[1]) as f:
        instrs = parse_instrs(f.read())
    defs_list, uses_list = get_vars(instrs)
    live_in, live_out = liveness(instrs, defs_list, uses_list)
    graph = build_interference(live_out, defs_list)
    colors = color_graph(graph, k)
    reg_names = [f"R{i}" for i in range(k)]
    print(f"Register allocation ({k} registers):\n")
    for var, color in sorted(colors.items()):
        reg = reg_names[color] if 0 <= color < k else "SPILL"
        print(f"  {var:10s} -> {reg}")
    spills = sum(1 for c in colors.values() if c < 0 or c >= k)
    if spills: print(f"\n{spills} variable(s) need spilling")

if __name__ == "__main__":
    main()
