# Uses python3
import sys
import math

DENOMS = [1, 3, 4]
COMPUTED = {}

def get_change(m):
    if m in COMPUTED:
        return COMPUTED[m]
    if m == 0:
        COMPUTED[m] = 0
        return 0
    if m < 0:
        COMPUTED[m] = math.inf
        return math.inf
    by_denom = [get_change(m - d) + 1 for d in DENOMS]
    best = min(by_denom)
    COMPUTED[m] = best
    return best

if __name__ == '__main__':
    m = int(sys.stdin.read())
    print(get_change(m))
    # print('computed:', COMPUTED)
