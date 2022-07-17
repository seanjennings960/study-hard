#Uses python3

import sys
import queue

def bipartite(adj):
    n = len(adj)
    if not n:
        return 1
    group = [None for _ in range(n)]

    q = queue.Queue()
    # Keep track of the first unvisited node.
    i = 0
    while i < n:
        if not q.empty():
            u = q.get()
        else:
            while i < n and group[i] is not None:
                # Find the next non-visted vertex
                i += 1
            if i == n:
                break
            u = i
            group[u] = 0
        for v in adj[u]:
            if group[u] == group[v]:
                # Vertex u has already been assigned
                # a group. If v has already been visited, make
                # sure it is not the same group as u. If it is,
                # then we are not bipartite.
                return 0
            elif group[v] is None:
                # v has not yet been visited. Assign the opposite group.
                group[v] = int(not group[u])
                q.put(v)
    return 1


if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n, m = data[0:2]
    data = data[2:]
    edges = list(zip(data[0:(2 * m):2], data[1:(2 * m):2]))
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a - 1].append(b - 1)
        adj[b - 1].append(a - 1)
    print(bipartite(adj))
