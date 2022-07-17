#Uses python3

import sys

sys.setrecursionlimit(200000)


def explore(adj, x, visited, post=None):
    visited[x] = True
    for i in adj[x]:
        if not visited[i]:
            explore(adj, i, visited, post)
    if post is not None:
        post.append(x)


def reverse_graph(adj):
    rev_adj = [[] for _ in range(len(adj))]
    for u in range(len(adj)):
        for v in adj[u]:
            rev_adj[v].append(u)
    return rev_adj


def search(adj):
    n = len(adj)
    post = []
    visited = [False for _ in range(n)]
    for x in range(n):
        if not visited[x]:
            explore(adj, x, visited, post)

    return post


def num_strongly_connected(adj):
    adj_rev = reverse_graph(adj)
    post_order = search(adj_rev)

    visited = [False for _ in range(len(adj))]

    num_connected = 0
    for x in post_order[::-1]:
        # Now search in reverse post order
        if not visited[x]:
            # If we've haven't visited it, that means
            # we lie a different strongly connected component
            # since we are searching from a new "sink". After
            # "removing" (by visitation) previous sinks.
            explore(adj, x, visited)
            num_connected += 1
    return num_connected


if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n, m = data[0:2]
    data = data[2:]
    edges = list(zip(data[0:(2 * m):2], data[1:(2 * m):2]))
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a - 1].append(b - 1)
    print(num_strongly_connected(adj))
