
import math
import sys


class PriorityQueue:
    def __init__(self, items, priorities):
        self.priorities = {
            i: p
            for i, p in zip(items, priorities)
        }

    def extract_min(self):
        i, _ = min(self.priorities.items(), key=lambda x: x[1])
        self.priorities.pop(i)
        return i

    def change_priority(self, v, new_p):
        self.priorities[v] = new_p

    def empty(self):
        return not bool(self.priorities)


def distance(adj, cost, s, t):
    n = len(adj)
    dist = [math.inf for _ in range(n)]
    dist[s] = 0

    q = PriorityQueue(list(range(n)), dist)

    while not q.empty():
        u = q.extract_min()
        for i, v in enumerate(adj[u]):
            d = dist[u] + cost[u][i]
            if dist[v] > d:
                dist[v] = d
                q.change_priority(v, d)
    if dist[t] != math.inf:
        return dist[t]
    return -1


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
    s, t = data[0] - 1, data[1] - 1
    print(distance(adj, cost, s, t))
