
import math
import sys

sys.setrecursionlimit(200000)


def relax(u, v, dist, w, prev):
    d = dist[u] + w
    if dist[v] > d:
        dist[v] = d
        prev[v] = u
        return True
    return False


def explore(adj, u, visited):
    visited[u] = True
    for v in adj[u]:
        if not visited[v]:
            explore(adj, v, visited)


def shortest_paths(adj, cost, s):
    n = len(adj)
    dist = [math.inf for _ in range(n)]
    prev = [None for _ in range(n)]
    dist[s] = 0

    for _ in range(n):
        relaxed = [False for _ in range(n)]
        for u in range(n):
            for i, v in enumerate(adj[u]):
                w = cost[u][i]
                if relax(u, v, dist, w, prev):
                    relaxed[u] = relaxed[v] = True

    no_shortest = [False for _ in range(n)]
    for u in range(n):
        if not relaxed[u]:
            # This node was not relaxed on the last cycle.
            continue
        # We now want to find any node that can reach the negative cycle.
        explore(adj, u, no_shortest)

    reachable = [dist[u] != math.inf for u in range(n)]
    # print(dist)
    # print(reachable)
    # print(no_shortest)

    return dist, reachable, no_shortest


if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n, m = data[0:2]
    data = data[2:]
    edges = list(zip(zip(data[0:(3 * m):3], data[1:(3 * m):3]),
                     data[2:(3 * m):3]))
    data = data[3 * m:]
    adj = [[] for _ in range(n)]
    cost = [[] for _ in range(n)]
    for ((a, b), w) in edges:
        adj[a - 1].append(b - 1)
        cost[a - 1].append(w)
    s = data[0]
    s -= 1
    distance, reachable, no_shortest = shortest_paths(adj, cost, s)
    for x in range(n):
        if not reachable[x]:
            print('*')
        elif no_shortest[x]:
            print('-')
        else:
            print(distance[x])
