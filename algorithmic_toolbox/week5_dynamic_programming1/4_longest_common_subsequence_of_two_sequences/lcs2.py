#Uses python3

import sys

##################################3
#    0  2  7  8
#
# 0  0->0->0->0
#    | \
# 2  0  1->1->1
#    |  | \| \
# 8  0  1->1  2


def lcs2(a, b):
    m, n = len(a), len(b)
    common = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            insert = common[i][j - 1]
            delete = common[i - 1][j]
            pair = common[i - 1][j - 1]
            if a[i - 1] == b[j - 1]:
                pair += 1
            common[i][j] = max([insert, delete, pair])
    return common[-1][-1]

if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))

    n = data[0]
    data = data[1:]
    a = data[:n]

    data = data[n:]
    m = data[0]
    data = data[1:]
    b = data[:m]

    print(lcs2(a, b))
