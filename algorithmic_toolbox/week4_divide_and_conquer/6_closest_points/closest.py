#Uses python3
import sys
import math


def dist(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2)

def minimum_distance(x, y, y_order=None):
    n = len(x)
    if n <= 1:
        return math.inf

    i = list(range(n))
    p = list(zip(i, x, y))

    if y_order is None:
        x_order = list(zip(*sorted(p, key=lambda x: x[1])))[0]
        y_order = list(zip(*sorted(p, key=lambda x: x[2])))[0]
    else:
        x_order = list(range(n))
    p = list(zip(*list(zip(*p))[1:]))

    mid = n // 2
    S1, S2 = ([p[i] for i in x_order[:mid]],
              [p[i] for i in x_order[mid:]])
    S1_y_ord, S2_y_ord = tuple(map(lambda i: rezero(i, n),
        ([y_order[i] for i in x_order[:mid]],
         [y_order[i] for i in x_order[mid:]])))
    d = min(minimum_distance(*zip(*S1), S1_y_ord),
            minimum_distance(*zip(*S2), S2_y_ord))

    x_split = (x[mid] + x[mid - 1]) / 2
    p = [p[i] for i in y_order]
    p_filt = list(filter(lambda p_i: (p_i[0] - x_split) < d, p))

    d_prime = math.inf
    for j in range(len(p_filt)):
        k_start = max(0, j - 7)
        for k in range(k_start, j):
            d_prime = min(d_prime,
                          dist(p_filt[j], p_filt[k]))
    return min(d, d_prime)



def rezero(indexes, max_i):
    counts = {i: 0 for i in range(max_i)}
    for i in indexes:
        counts[i] += 1
    sorted_ = [i for i in range(max_i) if counts[i] != 0]
    new_indexes = {x: i for i, x in enumerate(sorted_)}
    return [new_indexes[x] for x in indexes]






if __name__ == '__main__':
    # print(rezero([3, 5, 0, 6], 10))
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n = data[0]
    x = data[1::2]
    y = data[2::2]
    print("{0:.9f}".format(minimum_distance(x, y)))
