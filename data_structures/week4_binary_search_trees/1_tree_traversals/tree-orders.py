# python3

import sys, threading
from collections import deque
sys.setrecursionlimit(10**7) # max depth of recursion
threading.stack_size(2**27)  # new thread will get stack of such size

class TreeOrders:
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

    def inOrder(self):
        results = []
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
                results.append(self.key[i])
                if self.right[i] != -1:
                    i = self.right[i]
                else:
                    # Continue popping from the stack.
                    i = None
        return results

        # return (
        #     self.inOrder(self.left[i]) +
        #     [self.key[i]] +
        #     self.inOrder(self.right[i])
        # )

    def preOrder(self):
        results = []
        stack = deque()
        i = self.get_root()
        while i is not None or stack:
            if i is not None:
                results.append(self.key[i])
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
        return results


    # def preOrder(self, i=None):
    #     if i is None:
    #         i = self.get_root()
    #     if i == -1:
    #         return []
    #     return (
    #         [self.key[i]] +
    #         self.preOrder(self.left[i]) +
    #         self.preOrder(self.right[i])
    #     )

    def postOrder(self):
        results = []
        stack = deque()
        i = self.get_root()
        while i is not None or stack:
            # print('left_stack:', stack)
            if i is not None:
                # Start a new tree.
                stack.append(('left', i))
                if self.left[i] != -1:
                    i = self.left[i]
                else:
                    i = None
            else:
                finished, i = stack.pop()
                if finished == 'left':
                    stack.append(('right', i))
                    # We've finished the left hand side of the tree, now
                    # do the right.
                    if self.right[i] != -1:
                        i = self.right[i]
                    else:
                        i = None
                elif finished == 'right':
                    # We've now finished the right side of the tree, so can
                    # finally append to results.
                    results.append(self.key[i])
                    i = None
                else:
                    raise ValueError('unknown initial key...')
        return results
    # def postOrder(self, i=None):
    #     if i is None:
    #         i = self.get_root()
    #     if i == -1:
    #         return []
    #     return (
    #         self.postOrder(self.left[i]) +
    #         self.postOrder(self.right[i]) +
    #         [self.key[i]]
    #     )


def main():
    tree = TreeOrders()
    print(" ".join(str(x) for x in tree.inOrder()))
    print(" ".join(str(x) for x in tree.preOrder()))
    print(" ".join(str(x) for x in tree.postOrder()))


if __name__ == '__main__':
    # main()
    threading.Thread(target=main).start()
