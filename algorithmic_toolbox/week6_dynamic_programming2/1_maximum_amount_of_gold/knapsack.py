# Uses python3
import sys

OPTIMAL_WEIGHTS = {}


def optimal_weight(W, w, i):
    if (W, i) in OPTIMAL_WEIGHTS:
        return OPTIMAL_WEIGHTS[(W, i)]

    if W <= 0 or i <= 0:
        best = 0
    else:
        # Optimal weight if we leave the current item.
        best = optimal_weight(W, w, i - 1)
        w_i = w[i - 1]
        if W - w_i >= 0:
            # It's possible to take the (i - 1)th item, so we compare this
            # with leaving it.
            best = max(best, optimal_weight(W - w_i, w, i - 1) + w_i)
    OPTIMAL_WEIGHTS[(W, i)] = best
    return best


if __name__ == '__main__':
    input = sys.stdin.read()
    W, n, *w = list(map(int, input.split()))
    print(optimal_weight(W, w, n))
