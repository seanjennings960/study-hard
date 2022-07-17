import sys


def relax(u, v, w, dist):
    d = dist[u] + w
    if dist[v] > d:
        dist[v] = d
        return True
    return False


def negative_cycle(adj, cost):
    n = len(adj)
    if not n:
        return 0
    dist = [0 for _ in range(n)]

    for _ in range(n):
        edges_relaxed = False
        for u in range(n):
            for i, v in enumerate(adj[u]):
                w = cost[u][i]
                if relax(u, v, w, dist):
                    edges_relaxed = True
    # Return whether there were edges relaxed on the last iteration. This
    # indicates a negative cycle, since if there is no negative cycle, then
    # the Bellman-Ford algorithm should conclude after |V| - 1 iterations.
    return int(edges_relaxed)


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
    print(negative_cycle(adj, cost))
