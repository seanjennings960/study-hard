#!/usr/bin/python3

from collections import deque
import sys, threading

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
            [a, l, r] = map(int, sys.stdin.readline().split())
            self.key[i] = a
            self.left[i] = l
            self.right[i] = r
            if l != -1:
                self.parent[l] = i
            if r != -1:
                self.parent[r] = i
        self.level = self.get_levels()

    def get_root(self, i=0):
        p = self.parent[i]
        if p != -1:
            return self.get_root(self, p)
        return i

    def get_levels(self):
        levels = [-1 for _ in range(self.n)]
        for i in self.pre_order():
            p = self.parent[i]
            if p == -1:
                levels[i] = 0
            else:
                levels[i] = levels[self.parent[i]] + 1
        return levels

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

    def pre_order(self):
        if self.n < 1:
            return
        stack = deque()
        i = self.get_root()
        while i is not None or stack:
            if i is not None:
                yield i
                stack.append(i)
                if self.left[i] != -1:
                    i = self.left[i]
                else:
                    i = None
            else:
                # We are pulling from the stack, finish the right side.
                i = stack.pop()
                if self.right[i] != -1:
                    i = self.right[i]
                else:
                    i = None

    def is_search_tree(self):
        highest_key = None
        current_level = None
        for i in self.in_order():
            if highest_key is None or self.key[i] > highest_key:
                highest_key = self.key[i]
                current_level = self.level[i]
            elif self.key[i] == highest_key:
                if (current_level is not None and
                        self.level[i] <= current_level):
                    # Found an equal value in a lower level of the tree
                    # (closer to the root), meaning that an equal value is in
                    # a left subtree.
                    return False
                current_level = self.level[i]
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
