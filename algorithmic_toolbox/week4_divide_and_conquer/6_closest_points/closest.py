#Uses python3
import sys
import math


def dist(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2)

def minimum_distance(x, y):
    p = list(zip(x, y))
    return _minimum_distance(p)


def _minimum_distance(p):
    n = len(p)
    if n <= 1:
        # Base case: Rooted out by the mins.
        return math.inf

    p = sorted(p, key=lambda p_i: p_i[0])

    mid = n // 2
    S1, S2 = p[:mid], p[mid:]
    d = min(_minimum_distance(S1),
            _minimum_distance(S2))

    p = sorted(p, key=lambda p_i: p_i[1])
    # Filter out points that are gaurenteed out of range.
    x_split = (p[mid][0] + p[mid - 1][0]) / 2
    p_filt = list(filter(lambda p_i: (p_i[0] - x_split) < d, p))

    d_prime = math.inf
    for j in range(len(p_filt)):
        k_start = max(0, j - 7)
        for k in range(k_start, j):
            d_prime = min(d_prime,
                          dist(p_filt[j], p_filt[k]))
    return min(d, d_prime)



if __name__ == '__main__':
    # print(rezero([3, 5, 0, 6], 10))
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n = data[0]
    x = data[1::2]
    y = data[2::2]
    print("{0:.9f}".format(minimum_distance(x, y)))
