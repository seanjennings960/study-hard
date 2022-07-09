import math
# python3


def parent(i):
    return math.floor((i + 1) / 2) - 1

def left(i):
    return 2 * i + 1

def right(i):
    return 2 * i + 2

def is_leaf(i, n):
    return left(i) > n - 1

def sift_down(data, i, swaps):
    n = len(data)
    while not is_leaf(i, n):
        need_swap = False
        if right(i) > n - 1:
            if data[left(i)] < data[i]:
                # We only have a left node, and we need to swap.
                need_swap = True
                j = left(i)
        else:
            # We have both right and left so must check the smaller
            # against the parent.
            j = left(i) if data[left(i)] < data[right(i)] else right(i)
            if data[j] < data[i]:
                need_swap = True
        if need_swap:
            swaps.append((i, j))
            data[i], data[j] = data[j], data[i]
            i = j
        else:
            break


def is_heap(data):
    n = len(data)
    for i in range(n):
        for j in [left(i), right(i)]:
            if j <= n - 1 and data[i] > data[j]:
                return False
    return True

def build_heap(data):
    """Build a heap from ``data`` inplace.

    Returns a sequence of swaps performed by the algorithm.
    """
    # The following naive implementation just sorts the given sequence
    # using selection sort algorithm and saves the resulting sequence
    # of swaps. This turns the given array into a heap, but in the worst
    # case gives a quadratic number of swaps.
    #
    # TODO: replace by a more efficient implementation
    swaps = []
    n = len(data)
    height = math.floor(math.log(n, 2))

    start = 2 ** height - 2

    for i in range(start, -1, -1):
        sift_down(data, i, swaps)

    return swaps


def main():
    n = int(input())
    data = list(map(int, input().split()))
    assert len(data) == n

    swaps = build_heap(data)

    print(len(swaps))
    for i, j in swaps:
        print(i, j)
    assert len(swaps) <= 4 * n
    assert is_heap(data)


if __name__ == "__main__":
    main()
