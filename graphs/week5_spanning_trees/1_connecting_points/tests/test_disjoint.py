from connecting_points import DisjointSets
import sys

sys.setrecursionlimit(200000)


def test_sets():
    n = 1000
    sets = DisjointSets(n)

    for i in range(n - 1):
        assert sets.find(i) != sets.find(i + 1)

    for i in range(0, n - 1, 2):
        sets.union(i, i + 1)

    for i in range(n - 1):
        if i % 2 == 0:
            assert sets.find(i) == sets.find(i + 1)
        else:
            assert sets.find(i) != sets.find(i + 1)

    for i in range(n - 1):
        sets.union(i, i + 1)

    for i in range(n - 1):
        assert sets.find(i) == sets.find(i + 1)


if __name__ == '__main__':
    test_sets()
