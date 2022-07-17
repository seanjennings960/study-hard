import sys
import math


class DisjointSets:
    def __init__(self, n):
        self.n = n
        self.parent = list(range(n))
        self.rank = [0 for _ in range(n)]

    def find(self, x):
        if x >= self.n:
            raise ValueError(f'x {x} must be less than size {self.n}')
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def __str__(self):
        out = {}
        for i in range(self.n):
            p = self.find(i)
            if p not in out:
                out[p] = []
            out[p].append(i)
        return str(out)

    def union(self, x, y):
        p_x = self.find(x)
        p_y = self.find(y)
        if p_x == p_y:
            # Already in the same set, nothing to do.
            return

        if self.rank[p_x] > self.rank[p_y]:
            self.parent[p_y] = p_x
            self.rank[p_y] += 1
            return

        self.parent[p_x] = p_y
        self.rank[p_x] += 1


def construct_graph(x, y):
    edges = []
    costs = []
    n = len(x)

    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            edges.append((u, v))
            costs.append(math.sqrt(
                (x[u] - x[v]) ** 2 + (y[u] - y[v]) ** 2))

    return sort_edges(edges, costs)


def sort_edges(edges, costs):
    combined = list(zip(edges, costs))
    combined.sort(key=lambda x: x[1])
    return zip(*combined)


def clustering(x, y, k):
    n = len(x)
    edges, costs = construct_graph(x, y)
    sets = DisjointSets(n)

    edges_found = 0
    for (u, v), c in zip(edges, costs):
        if sets.find(u) != sets.find(v):
            if edges_found >= n - k:
                return c
            sets.union(u, v)
            edges_found += 1
    return 0


if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n = data[0]
    data = data[1:]
    x = data[0:2 * n:2]
    y = data[1:2 * n:2]
    data = data[2 * n:]
    k = data[0]
    print("{0:.9f}".format(clustering(x, y, k)))
