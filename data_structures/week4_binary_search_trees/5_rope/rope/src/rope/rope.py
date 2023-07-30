# python3

import math

# import sys
from typing import Optional, Union

Child = Optional[Union["Node", str]]


class Node:
    def __init__(
            self, left: Child, right: Child,
            parent: Optional["Node"], key: int):
        self.right = right
        self.left = left
        self.parent = parent
        if not isinstance(key, int):
            msg = "badddd"
            raise RuntimeError(msg)
        self.key = key

    def _str_from_child(self, c: Child) -> str:
        if isinstance(c, Node):
            return str(c)
        elif isinstance(c, str):
            return c
        else:
            return ""

    def __str__(self):
        return (self._str_from_child(self.left) +
                self._str_from_child(self.right))

    def __repr__(self):
        return f"""
            NODE:
                key: {self.key}
                left: {self.left!r}
                right: {self.right!r}
        """




class Rope:

    def __init__(self, s):
        self.root = Node(s, None, None, len(s))

    def __str__(self):
        return str(self.root)

    def split(self, x: int):
        self.root, right = self._split(self.root, x)
        return self, Rope.from_node(right)

    def concat(self, r: "Rope") -> "Rope":
        return Rope.from_node(self._concat(self.root, r.root))

    def cut(self, i, j):
        left, right = self._split(self.root, i)
        cut, right = self._split(right, j - i + 1)
        merged = self._concat(left, right)
        return (cut, merged)

    def paste(self, s, cut, k):
        left, right = self._split(s, k)
        left = self._concat(left, cut)
        return self._concat(left, right)

    def process(self, i, j, k):
        cut, merged = self.cut(i, j)
        self.root = self.paste(merged, cut, k)

    def set_left(self, p: Node, left: Child):
        p.left = left
        if isinstance(left, Node):
            left.parent = p

    def set_right(self, p: Node, right: Child):
        p.right = right
        if isinstance(right, Node):
            right.parent = p

    def swap_parents(self, old_child: Node, new_child: Node):
        p = old_child.parent
        new_child.parent = p
        if p is not None:
            if p.left == old_child:
                p.left = new_child
            elif p.right == old_child:
                p.right = new_child
            else:
                msg = "parent/child broken!"
                raise RuntimeError(msg)

    def zig(self, a: Node):
        old_p = a.parent
        if old_p is None:
            # We are already root.
            return
        if old_p.parent is not None:
            msg = "Must only zig on a node just before root"
            raise RuntimeError(msg)
        if a == old_p.left:
            c = a.right
            # Update values for old parent who is now right child of a
            self.set_left(old_p, c)
            self.set_right(a, old_p)
            old_p.key -= a.key
            # Now set a as new root
            a.parent = None
        elif a == old_p.right:
            c = a.left
            # Old parent now becomes the left node of a.
            self.set_right(old_p, c)
            self.set_left(a, old_p)
            # A is new root, and since it lost c as a left child, it's
            # key must change
            a.parent = None
            a.key += old_p.key
        else:
            msg = "Parent/child double link broken!"
            raise RuntimeError(msg)

    def zig_zig(self, a: Node):
        b = a.parent
        if b is None:
            msg = "ran zig_zig on root!"
            raise RuntimeError(msg)
        c = b.parent
        if c is None:
            msg = "Node a must have grandparent to zig_zig!"
            raise RuntimeError(msg)
        if a == b.left:
            if b != c.left:
                msg = "Bad zig_zig case!"
                raise RuntimeError(msg)
            d = a.right
            e = b.right
            self.swap_parents(c, a)
            self.set_right(a, b)
            self.set_right(b, c)
            self.set_left(b, d)
            self.set_left(c, e)
            c.key -= b.key
            b.key -= a.key
        elif a == b.right:
            if b != c.right:
                msg = "Bad zig zig case!"
                raise RuntimeError(msg)
            d = a.left
            e = b.left
            self.swap_parents(c, a)
            # Update b first.
            self.set_left(a, b)
            self.set_left(b, c)
            self.set_right(b, d)
            self.set_right(c, e)
            b.key += c.key
            a.key += b.key
        else:
            msg = "parent/child broken!"
            raise RuntimeError(msg)

    def zig_zag(self, a: Node):
        b = a.parent
        if b is None:
            msg = "Ran zig_zag on root!"
            raise RuntimeError(msg)
        c = b.parent
        if c is None:
            msg = "target of zigzag must have grandparent"
            raise RuntimeError(msg)
        if a == b.right:
            if b != c.left:
                msg = "bad zigzag case!"
                raise RuntimeError(msg)
            left = a.left
            right = a.right
            self.swap_parents(c, a)
            self.set_left(a, b)
            self.set_right(a, c)
            self.set_right(b, left)
            self.set_left(c, right)
            a.key += b.key
            c.key -= a.key
        elif a == b.left:
            if b != c.right:
                msg = "Bad zig-zag case!"
                raise RuntimeError(msg)
            left = a.left
            right = a.right
            self.swap_parents(c, a)
            # Update B first since it's key depends on A
            self.set_left(a, c)
            self.set_right(a, b)
            self.set_left(b, right)
            self.set_right(c, left)
            b.key -= a.key
            a.key += c.key
        else:
            msg = "parent/child broken!"
            raise RuntimeError(msg)


    def choose_zig(self, n: Node):
        p = n.parent
        # We assume n has a parent.
        gp = p.parent
        if gp is None:
            return self.zig
        if p == gp.left and n == p.left:
            return self.zig_zig
        elif p == gp.right and n == p.right:
            return self.zig_zig
        elif p == gp.left and n == p.right:
            return self.zig_zag
        elif p == gp.right and n == p.left:
            return self.zig_zag
        else:
            msg = "Linking broken!"
            raise RuntimeError(msg)



    def splay(self, n: Node):
        if n.parent is None:
            # We are now root, our work here is done.
            return
        op = self.choose_zig(n)
        op(n)
        # Continue to splay until n is root!
        self.splay(n)


    def insert_split(self, n: Optional[Node], x: int):
        if n is None:
            msg = f"x {x} is out of range"
            raise IndexError(msg)
        if x == n.key:
            # We already have a split!
            self.splay(n)
            return n
        elif x > n.key:
            diff = x - n.key
            if isinstance(n.right, str):
                left = n.right[:diff]
                right = n.right[diff:]
                new_node = Node(left, right, n, len(left))
                n.right = new_node
                self.splay(new_node)
                return new_node
            return self.insert_split(n.right, diff)
        elif x < n.key:
            if isinstance(n.left, str):
                left = n.left[:x]
                right = n.left[x:]
                new_node = Node(left, right, n, len(left))
                n.left = new_node
                self.splay(new_node)
                return new_node
            return self.insert_split(n.left, x)
        msg = "huh???"
        raise RuntimeError(msg)


    def _split(self, n: Node, x: int):
        left = self.insert_split(n, x)
        # We have now created the insertion point and splayed it to
        # the top. Now, it remains to split the right subtree into
        # its own tree.
        if left.right is None:
            right = Node("", None, None, 0)
        else:
            right = left.right
            left.right = None
            right.parent = None
        return (left, right)


    def find(self, n: Node, x: int):
        if x == n.key:
            self.splay(n)
            return n
        elif x < n.key:
            if isinstance(n.left, Node):
                return self.find(n.left, x)
        # x > n.key
        elif isinstance(n.right, Node):
            return self.find(n.right, x - n.key)
        # We've reached a leaf node.
        self.splay(n)
        return n

    def _concat(self, a: Node, b: Node):
        r = self.find(a, math.inf)
        if r.right is not None:
            msg = "What? string got inserted greater than rope length..."
            raise RuntimeError(msg)
        r.right = b
        b.parent = r
        return r

    @classmethod
    def from_node(cls, n: Node):
        rope = cls("")
        rope.root = n
        return rope



# if __name__ == '__main__':

# rope = Rope(sys.stdin.readline().strip())
# q = int(sys.stdin.readline())
# for _ in range(q):
#     i, j, k = map(int, sys.stdin.readline().strip().split())
#     rope.process(i, j, k)
# print(rope.result())
