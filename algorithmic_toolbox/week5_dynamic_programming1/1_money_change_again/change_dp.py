# Uses python3
import sys
import math

DENOMS = [1, 3, 4]
COMPUTED = {}

def get_change(m: int):
    if m <= 0:
        raise ValueError('input out of range, must be greater than 0.')
    changes = [0] * (m + 1)
    for i in range(1, m + 1):
        best = math.inf
        for denom in DENOMS:
            if i - denom >= 0:
                best = min(best, changes[i - denom] + 1)
        changes[i] = best
    return changes[-1]

if __name__ == '__main__':
    m = int(sys.stdin.read())
    print(get_change(m))
    # print('computed:', COMPUTED)
