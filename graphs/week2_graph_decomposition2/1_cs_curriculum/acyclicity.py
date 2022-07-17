#Uses python3

import sys


class PostOrder:
    def __init__(self, n):
        self.counter = 0
        self.order = [-1 for _ in range(n)]

    def set(self, x):
        self.order[self.counter] = x
        self.counter += 1


def explore(adj, x, visited, post=None):
    visited[x] = True
    for i in adj[x]:
        if not visited[i]:
            explore(adj, i, visited, post)
    if post is not None:
        post.set(x)


def reverse_graph(adj):
    rev_adj = [[] for _ in range(len(adj))]
    for u in range(len(adj)):
        for v in adj[u]:
            rev_adj[v].append(u)
    return rev_adj


def search(adj):
    n = len(adj)
    post = PostOrder(n)
    visited = [False for _ in range(n)]
    for x in range(n):
        if not visited[x]:
            explore(adj, x, visited, post)

    return post.order


def acyclic(adj):
    adj_rev = reverse_graph(adj)
    post_order = search(adj_rev)

    visited = [False for _ in range(len(adj))]

    for x in post_order[::-1]:
        # Now search in reverse post order
        if visited[x]:
            # If we've already visited it, that means
            # we lie in the same strongly connected component
            # as some previously explored node, since we are
            # searching in reverse post order.
            # Return 1 to which means we have a cycle.
            return 1
        explore(adj, x, visited)
    return 0


if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n, m = data[0:2]
    data = data[2:]
    edges = list(zip(data[0:(2 * m):2], data[1:(2 * m):2]))
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a - 1].append(b - 1)
    print(acyclic(adj))
