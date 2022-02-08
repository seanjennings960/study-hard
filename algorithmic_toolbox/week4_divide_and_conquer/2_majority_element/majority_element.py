# Uses python3
import sys

def has_majority_element(a):
    n = len(a)
    counts = {}
    for a_i in a:
        if a_i not in counts:
            counts[a_i] = 0
        counts[a_i] += 1

    for count in counts.values():
        if count > n / 2:
            return True
    return False

if __name__ == '__main__':
    input = sys.stdin.read()
    n, *a = list(map(int, input.split()))
    if has_majority_element(a):
        print(1)
    else:
        print(0)
