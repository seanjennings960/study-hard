# Uses python3
import sys
import itertools


def backtrace(values, items):
    n = len(items)
    selected = []
    current_w = values[n][-1]
    for i in range(n, 0, -1):
        w = items[i - 1]
        if values[i][current_w] == values[i - 1][current_w]:
            # Don't need to take it.
            selected.append(0)
        else:
            selected.append(1)
            current_w -= w
    return selected[::-1]

def value_table(W, items):
    n = len(items)
    value = [[0 for _ in range(W + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, W + 1):
            value[i][j] = value[i - 1][j]
            current_w = items[i - 1]
            if j - current_w >= 0:
                # If we don't exceed the current weight limit of j.
                value[i][j] = max(
                    value[i][j],
                    value[i - 1][j - current_w] + current_w)
    return value


def partition(A, n_part):
    if n_part == 1:
        return 1
    if sum(A) % n_part != 0:
        return 0
    # Each partition must not exceed an even division.
    n = len(A)
    even = sum(A) // n_part
    values = value_table(even, A)

    max_weight = values[n][even]
    if max_weight != even:
        # The partition can't add up to the even amount.
        return 0

    # Now, backtrace the table to compute what's left and see if that
    # can be evenly partition into one less part.
    selected = backtrace(values, A)
    remainder = [A[i] for i, included in enumerate(selected)
                 if not included]
    return partition(remainder, n_part - 1)




if __name__ == '__main__':
    input = sys.stdin.read()
    n, *A = list(map(int, input.split()))
    print(partition(A, 3))

