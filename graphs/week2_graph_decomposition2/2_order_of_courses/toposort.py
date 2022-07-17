#Uses python3

import sys

def explore(adj, x, visited, order):
    visited[x] = True
    for i in adj[x]:
        if not visited[i]:
            explore(adj, i, visited, order)
    order.append(x)


def toposort(adj):
    order = []
    visited = [False for _ in range(len(adj))]
    for x in range(len(adj)):
        if not visited[x]:
            explore(adj, x, visited, order)

    # Return the reversed post order
    return order[::-1]


if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n, m = data[0:2]
    data = data[2:]
    edges = list(zip(data[0:(2 * m):2], data[1:(2 * m):2]))
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a - 1].append(b - 1)
    order = toposort(adj)
    for x in order:
        print(x + 1, end=' ')

