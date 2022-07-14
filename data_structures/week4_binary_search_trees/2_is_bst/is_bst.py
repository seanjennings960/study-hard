#!/usr/bin/python3

import sys, threading
from collections import deque

sys.setrecursionlimit(10**7) # max depth of recursion
threading.stack_size(2**25)  # new thread will get stack of such size

class Tree:
    def __init__(self):
        self.n = int(sys.stdin.readline())
        self.key = [0 for i in range(self.n)]
        self.left = [0 for i in range(self.n)]
        self.right = [0 for i in range(self.n)]
        self.parent = [-1 for i in range(self.n)]
        for i in range(self.n):
            [a, b, c] = map(int, sys.stdin.readline().split())
            self.key[i] = a
            self.left[i] = b
            self.right[i] = c
            self.parent[b] = self.parent[c] = i

    def get_root(self, i=0):
        p = self.parent[i]
        if p != -1:
            return self.get_root(self, p)
        return i

    def in_order(self):
        if self.n < 1:
            return
        stack = deque()
        i = self.get_root()
        while i is not None or stack:
            if i is not None:
                stack.append(i)
                if self.left[i] != -1:
                    i = self.left[i]
                else:
                    # Now inOrder(left[i]) returns None and we need
                    # to start popping from stack
                    i = None
            else:
                i = stack.pop()

                yield i

                if self.right[i] != -1:
                    i = self.right[i]
                else:
                    # Continue popping from the stack.
                    i = None

    def find(self, k, i=None):
        if i is None:
            i = self.get_root()
        if k == self.key[i]:
            return i
        elif k < self.key[i]:
            # print(f'find({k}) less than {i}')
            if self.left[i] == -1:
                return i
            return self.find(k, self.left[i])
        else:
            # print(f'find({k}) greater than {i}')
            if self.right[i] == -1:
                return i
            return self.find(k, self.right[i])


    def is_search_tree(self):
        highest_key = None
        for i in self.in_order():
            if highest_key is None or self.key[i] > highest_key:
                highest_key = self.key[i]
            else:
                # We are not monotonically increasing
                return False
        return True


def main():
    tree = Tree()
    if tree.is_search_tree():
        print("CORRECT")
    else:
        print("INCORRECT")

threading.Thread(target=main).start()
