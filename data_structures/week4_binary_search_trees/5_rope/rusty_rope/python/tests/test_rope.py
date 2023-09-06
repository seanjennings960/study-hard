from typing import Optional, Union

import pytest

from rope import Node, Rope

MockChild = Union["MockNode", str]

class MockNode:
    def __init__(self, key: int, left: Optional[MockChild] = None,
                right: Optional[MockChild] = None):
        self.key = key
        self.left = left
        self.right = right

def assert_node(n, m):
    if n is None or m is None:
        assert n is None and m is None
    elif isinstance(n, str) or isinstance(m, str):
        assert isinstance(n, str) and isinstance(m, str)
        assert n == m
    else:
        assert n.key == m.key
        assert_node(n.left, m.left)
        if isinstance(n.left, Node):
            assert n.left.parent == n

        assert_node(n.right, m.right)
        if isinstance(n.right, Node):
            assert n.right.parent == n


def test_splay():
    s = "helloworld"
    r = Rope(s)
    assert str(r.root) == s
    ind = 5
    n = r.insert_split(r.root, ind)
    # Zig left -> right
    assert_node(n, MockNode(5,
        "hello", MockNode(5, "world")
    ))
    n = r.insert_split(n, 7)
    # Zig-zag right-left
    assert_node(n, MockNode(7,
        MockNode(5, "hello", "wo"),
        MockNode(3, "rld")
    ))
    n = n.right
    r.splay(n)
    # Zig right -> left
    pre_zig_zig = MockNode(10,
        MockNode(7,
            MockNode(5, "hello", "wo"),
            "rld")
    )
    assert_node(n, pre_zig_zig)
    n = n.left.left
    # Zig-zig left -> right
    r.splay(n)
    assert_node(n, MockNode(5,
        "hello",
        MockNode(2,
            "wo",
            MockNode(3, "rld")
        )
    ))
    n = n.right.right
    r.splay(n)
    # Zig-zig right -> left
    assert_node(n, pre_zig_zig)

    n = r.insert_split(n, 6)
    # Insert + multi-level zig zag left-right, then zig
    assert_node(n, MockNode(6,
        MockNode(5, "hello", "w"),
        MockNode(4, MockNode(1,
            "o",
            "rld"
        ))
    ))

    n = r.insert_split(n, 8)
    assert_node(n, MockNode(8,
        MockNode(6,
            MockNode(5, "hello", "w"),
            MockNode(1, "o", "r")
        ),
        MockNode(2, "ld")
    ))


def test_rope():
    s = "hello world"
    r = Rope(s)
    assert str(r) == s

    ind = 6
    r1, r2 = r.split(ind)
    assert str(r1) == s[:ind]
    assert str(r2) == s[ind:]
    r3 = r1.concat(r2)
    assert str(r3) == s


@pytest.mark.parametrize(
    ("start", "ops", "result"), [
        ("hlelowrold", [
            (1, 1, 2),
            (6, 6, 7)
        ], "helloworld"),
        ("abcdef", [
            (0, 1, 1),
            (4, 5, 0)
        ], "efcabd")
    ]
)
def test_cut_and_paste(start, ops, result):
    r = Rope(start)
    for (i, j, k) in ops:
        r.process(i, j, k)
    assert str(r) == result

