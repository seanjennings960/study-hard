import math

M = 1_000_000_001


def left_descendent(n):
    if n is None:
        return None
    while n.left is not None:
        n = n.left
    return n


def right_ancestor(n):
    k = n.key
    while n.parent is not None and n.key <= k:
        # Go up until the first ancestor greater than
        # original n.
        n = n.parent
    if n.key > k:
        return n
    # Original n was the greatest in the tree.
    return None


def next_(n):
    if n.right is not None:
        return left_descendent(n.right)
    return right_ancestor(n)


def cut_left(n):
    l_ = n.left
    if l_ is None:
        # Nothing to do.
        return l_, n
    l_.parent, n.left = None, None
    n.update_sum()
    return l_, n


def cut_right(n):
    r = n.right
    if r is None:
        # Nothing to do
        return n, r
    r.parent, n.right = None, None
    n.update_sum()
    return n, r


def find(n, k):
    while n is not None:
        if k == n.key:
            return n
        elif k < n.key:
            if n.left is None:
                return n
            n = n.left
        else:
            if n.right is None:
                return n
            n = n.right


def update_parents(nodes, parents):
    for n, p in zip(nodes, parents):
        if n is not None:
            n.parent = p


class Node:
    def __init__(self, key, parent, left, right, sum):
        self.key, self.parent, self.left, self.right, self.sum = (
            key, parent, left, right, sum)

    def update_sum(self):
        """We assume that left and right nodes are up to date."""
        l_, r = self.left, self.right
        l_sum = 0 if l_ is None else l_.sum
        r_sum = 0 if r is None else r.sum
        self.sum = l_sum + r_sum + self.key

    def as_string(self, full=True):
        attrs = (['key', 'parent', 'left', 'right', 'sum']
                 if full else ['key'])
        attrs_format = ', '.join(
            [f'{a}={str(getattr(self, a))}' for a in attrs])
        return f'Node({attrs_format})'

    def __str__(self):
        return self.as_string(full=False)


class SplayTree:
    def __init__(self, root=None):
        self.update_root(root)

    def update_root(self, n, validation='strict'):
        if validation == 'strict':
            if n is not None and n.parent is not None:
                raise ValueError('Root node must not have a parent.')
            self.root = n
        elif validation == 'conditional':
            # Used for splaying. Don't allow root to be None.
            if n is None:
                raise ValueError("root can't be None while splaying")
            if n.parent is None:
                self.root = n
        elif validation == 'force':
            # This is used for deletion mostly. Here the tree can become
            # empty again and that's ok.
            self.root = n
            if n is not None:
                # We just set the root parent to None if it's non-empty
                n.parent = None
        else:
            raise ValueError(f'Unknown validation {validation}')

    def __str__(self):
        return self.as_string()

    def as_string(self, attr='key'):
        if self.root is None:
            return '[Empty tree]'

        q = [self.root]
        out = ''
        while q:
            next_level = []
            has_item = False
            row = [str(getattr(i, attr)) if i is not None else ' '
                   for i in q]
            for i in q:
                if i is not None:
                    next_level.extend([i.left, i.right])
                    if (next_level[-1] is not None or
                            next_level[-2] is not None):
                        has_item = True
                else:
                    next_level.extend([None, None])
            q = next_level if has_item else []
            out += ' '.join(row)
            if has_item:
                out += '\n'
        return out

    def _detect_case(self, n):
        if n.parent is None:
            assert False, 'should not splay root!'
        p = n.parent
        gp = p.parent
        if gp is None:
            return 'zig'
        first_step = n == p.left
        if not first_step:
            assert n == p.right, 'pointer relation broken'
        second_step = p == gp.left
        if not second_step:
            assert p == gp.right, 'pointer relation broken'
        if first_step == second_step:
            return 'zig-zig'
        else:
            return 'zig-zag'

    def _zig(self, n, p):
        if n == p.left:
            a, b, c = n.left, n.right, p.right
            n.left, n.right = a, p
            p.left, p.right = b, c
        elif n == p.right:
            a, b, c = p.left, n.left, n.right
            p.left, p.right = a, b
            n.left, n.right = p, c
        else:
            raise RuntimeError('Pointer mismatch in zig, n -> parent broken\n'
                               f'n = {n}\n'
                               f'p = {p}')
        update_parents([p, b], [n, p])
        self.update_root(n, 'force')
        for i in [p, n]:
            i.update_sum()

    def _update_child(self, old, new):
        p = old.parent
        if p is not None:
            if p.left == old:
                p.left = new
            elif p.right == old:
                p.right = new

    def _zig_zig(self, n, p, gp):
        if n == p.left:
            a, b = n.left, n.right
            c, d = p.right, gp.right
            n.left, n.right = a, p
            p.left, p.right = b, gp
            gp.left, gp.right = c, d
            update_parents([b, c], [p, gp])
        elif n == p.right:
            a, b = gp.left, p.left
            c, d = n.left, n.right
            n.left, n.right = p, d
            p.left, p.right = gp, c
            gp.left, gp.right = a, b
            update_parents([b, c], [gp, p])
        else:
            raise RuntimeError('Pointer mismatch')

        self._update_child(gp, n)
        n.parent, p.parent, gp.parent = gp.parent, n, p
        self.update_root(n, 'conditional')
        for i in [gp, p, n]:
            i.update_sum()

    def _zig_zag(self, n, p, gp):
        b, c = n.left, n.right
        if n == p.left:
            a, d = gp.left, p.right
            n.left, n.right = gp, p
            gp.left, gp.right = a, b
            p.left, p.right = c, d
            update_parents([b, c], [gp, p])
        elif n == p.right:
            a, d = p.left, gp.right
            n.left, n.right = p, gp
            p.left, p.right = a, b
            gp.left, gp.right = c, d
            update_parents([b, c], [p, gp])
        else:
            raise RuntimeError('Pointer mismatch')
        self._update_child(gp, n)
        n.parent, p.parent, gp.parent = gp.parent, n, n
        self.update_root(n, 'conditional')
        for i in [gp, p, n]:
            i.update_sum()

    def splay(self, n):
        if n is None or n.parent is None:
            # Either we have an empty tree, or are at the root.
            return

        while n.parent is not None:
            case = self._detect_case(n)
            p = n.parent
            gp = p.parent
            if case == 'zig':
                self._zig(n, p)
            elif case == 'zig-zag':
                self._zig_zag(n, p, gp)
            elif case == 'zig-zig':
                self._zig_zig(n, p, gp)
            else:
                raise RuntimeError(f'invalid case {case}')

    def add(self, k):
        if self.root is None:
            self.update_root(Node(k, None, None, None, k))

        n = self.find(k, splay=False)
        if n is not None and k == n.key:
            # Already in tree.
            return
        elif k < n.key:
            n.left = Node(k, n, None, None, k)
        else:
            n.right = Node(k, n, None, None, k)

        while n is not None:
            # Only nodes up the tree have their sum affected.
            n.update_sum()
            n = n.parent

        # Call find to splay tree.
        self.find(k)

    def del_(self, k):
        n = self.find(k, splay=False)
        if n is None or n.key != k:
            # Doesn't exist in tree already.
            return
        s = next_(n)
        if s is None:
            # n is the greatest in the tree
            self.splay(n)
            l_ = n.left
            self.update_root(l_, 'force')
        else:
            # Remove n and replace with it's successor, now directly to
            # the right.
            self.splay(s)
            self.splay(n)
            l_ = n.left
            s.left = l_
            if l_ is not None:
                l_.parent = s
            self.update_root(s, 'force')
            s.update_sum()

    def find(self, k, start=None, splay=True):
        if start is None:
            start = self.root
        n = find(start, k)
        if splay:
            self.splay(n)
        return n

    def split(self, k, match='left'):
        """
        Split tree at value k.

        Arguments:
            k: value to split at
            match: what to do in case the tree contains an exact match k.
                if "left", the node matching k will be included in the left
                split; if "right" the node will be included in the right
                split. Other values will raise a ValueError.
        """
        l, r = self._split(k, match)
        return SplayTree(l), SplayTree(r)

    def _split(self, k, match):
        n = self.find(k)
        if n is None:
            # Tree is empty
            return None, None
        if k > n.key:
            return cut_right(n)
        elif k < n.key:
            return cut_left(n)
        elif match == 'left':
            return cut_right(n)
        elif match == 'right':
            return cut_left(n)
        else:
            raise ValueError('Unknown match value. Must be "left" or "right"')

    def merge(self, other: 'SplayTree'):
        """
        Merge with another tree.

        Arguments:
            r: BST with all values greater than all values of self.
        """
        r = other.root
        if r is None:
            # Nothing to do.
            return self

        # Move the largest element to the root
        n = self.find(math.inf)
        if n is None:
            # Nothing to do.
            return other
        n.right, r.parent = r, n
        n.update_sum()
        return self

    def sum(self, lower, upper):
        l, i = self.split(lower, match='right')
        m, r = i.split(upper, match='left')
        total = 0 if m.root is None else m.root.sum
        merged = l.merge(m).merge(r)
        self.root = merged.root
        return total

    def __contains__(self, k):
        found = self.find(k, splay=False)
        return found is not None and found.key == k


class Sum:

    """"Keep track of sum dependence."""

    def __init__(self):
        self.total = 0

    def update(self, total):
        self.total = total

    def transform(self, v):
        return (v + self.total) % M


OP_MAP = {
    '+': 'add',
    '-': 'del',
    's': 'sum',
    '?': 'find'
}


def format_op(op, vals):
    vals = list(map(str, vals))
    return OP_MAP[op] + '(' + ', '.join(vals) + ')'


DEBUG = False


def debug_prints(i, tree, op, vals, checksum):
    print(f'Step {i}')
    print(format_op(op, vals))
    # print('Original', format_op(op, vals))
    # print('Transformed', format_op(op, vals))
    print('Tree before')
    print(tree)
    if tree.root is None:
        print('tree root None')
    else:
        print('tree sum:', tree.root.sum)
    print('Checksum:', checksum)
    print()
    # print('Tree sum')
    # print(tree.as_string('sum'))


def run_op(tree, op, vals, sum_, checksum):
    if op == '+':
        if not vals[0] in tree:
            checksum += vals[0]
        tree.add(vals[0])
    elif op == '-':
        if vals[0] in tree:
            checksum -= vals[0]
        tree.del_(vals[0])
    elif op == '?':
        k = vals[0]
        n = tree.find(k)
        if n is not None and n.key == k:
            return checksum, 'Found'
        else:
            return checksum, 'Not found'
    elif op == 's':
        s = tree.sum(vals[0], vals[1])
        sum_.update(s)
        return checksum, s
    return checksum, None


def main():
    sum_ = Sum()
    num_actions = int(input())
    tree = SplayTree()
    resp = []
    checksum = 0
    for i in range(num_actions):
        op, *vals = input().split()
        original_vals = list(map(int, vals))
        vals = list(map(sum_.transform, original_vals))
        if DEBUG:
            debug_prints(i, tree, op, vals, checksum)
        if tree.root is None:
            assert checksum == 0
        else:
            assert checksum == tree.root.sum, \
                   f'Checksum {checksum} != tree sum {tree.root.sum}'
        checksum, output = run_op(tree, op, vals, sum_, checksum)
        if DEBUG:
            print('Tree after')
            print(tree)
        if output is not None:
            if DEBUG:
                print(output)
            resp.append(output)
    if DEBUG:
        print('\n\nRESPONSE')
    for r in resp:
        print(r)


if __name__ == '__main__':
    main()
