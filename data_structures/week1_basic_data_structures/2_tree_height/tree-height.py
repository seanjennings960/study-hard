# python3

import sys, threading
sys.setrecursionlimit(10**7) # max depth of recursion
threading.stack_size(2**27)  # new thread will get stack of such size

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def height(self):
        if not self.children:
            return 1
        return max([c.height() for c in self.children]) + 1

    def __str__(self):
        return str(self.value)


class Tree:
    def __init__(self):
        self.n = int(sys.stdin.readline())
        self.parent = list(map(int, sys.stdin.readline().split()))
        self.nodes = [Node(i) for i in range(self.n)]
        self.root = None
        for i in range(self.n):
            p = self.parent[i]
            if p == -1:
                if self.root is not None:
                    raise ValueError('multiple root nodes!')
                self.root = self.nodes[i]
            else:
                self.nodes[p].children.append(self.nodes[i])

    def compute_height(self):
        return self.root.height()
def main():
  tree = Tree()
  print(tree.compute_height())

threading.Thread(target=main).start()
