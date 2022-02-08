# Uses python3
import sys

def get_optimal_value(capacity, weights, values):
    v_per_w = [(i, v / w) for i, (v, w) in enumerate(zip(values, weights))]
    indexes, v_per_w = zip(*sorted(v_per_w, key=lambda x: x[1], reverse=True))

    total_weight = 0
    total_value = 0
    item = 0
    while total_weight < capacity and item < len(v_per_w):
        v = values[indexes[item]]
        w = weights[indexes[item]]
        if total_weight + w < capacity:
            total_weight += w
            total_value += v
            item += 1
        else:
            total_value += (capacity - total_weight) * v / w
            break

    return total_value


if __name__ == "__main__":
    data = list(map(int, sys.stdin.read().split()))
    n, capacity = data[0:2]
    values = data[2:(2 * n + 2):2]
    weights = data[3:(2 * n + 2):2]
    opt_value = get_optimal_value(capacity, weights, values)
    print("{:.10f}".format(opt_value))
