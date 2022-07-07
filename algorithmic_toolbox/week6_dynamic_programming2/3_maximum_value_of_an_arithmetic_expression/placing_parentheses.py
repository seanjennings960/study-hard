# Uses python3
def evalt(a, b, op):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    else:
        assert False


def get_max(max_S, min_S, i, j, ops):
    maxes = [
        max(evalt(max_S[i][k], max_S[k + 1][j], ops[k]),
            evalt(max_S[i][k], min_S[k + 1][j], ops[k]),
            evalt(min_S[i][k], max_S[k + 1][j], ops[k]),
            evalt(min_S[i][k], min_S[k + 1][j], ops[k]))
        for k in range(i, j)
    ]
    return max(maxes)


def get_min(max_S, min_S, i, j, ops):
    mins = [
        min(evalt(max_S[i][k], max_S[k + 1][j], ops[k]),
            evalt(max_S[i][k], min_S[k + 1][j], ops[k]),
            evalt(min_S[i][k], max_S[k + 1][j], ops[k]),
            evalt(min_S[i][k], min_S[k + 1][j], ops[k]))
        for k in range(i, j)
    ]
    return min(mins)


def get_maximum_value(dataset):
    digits = [int(d) for d in dataset[::2]]
    ops = [o for o in dataset[1::2]]

    n = len(digits)
    max_S = [[0] * n for _ in range(n)]
    min_S = [[0] * n for _ in range(n)]
    for i in range(n):
        # Initialize single value subexpressions
        max_S[i][i] = min_S[i][i] = digits[i]

    for len_sub in range(1, n):
        for i in range(n - len_sub):
            j = i + len_sub
            max_S[i][j] = get_max(max_S, min_S, i, j, ops)
            min_S[i][j] = get_min(max_S, min_S, i, j, ops)

    return max_S[0][n - 1]


if __name__ == "__main__":
    print(get_maximum_value(input()))
