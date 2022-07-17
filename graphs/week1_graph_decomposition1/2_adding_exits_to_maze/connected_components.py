#Uses python3

import sys

def explore(adj, x, visited):
    visited[x] = True
    for i in adj[x]:
        if not visited[i]:
            explore(adj, i, visited)


def number_of_components(adj):
    n = len(adj)
    visited = [False for _ in range(n)]
    cc = 0
    for x in range(n):
        if not visited[x]:
            cc += 1
            explore(adj, x, visited)
    #write your code here
    return cc

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
    print(number_of_components(adj))
