# Uses python3
import math
import sys

def best_previous(min_ops, i):
    div3 = min_ops[i // 3] if i % 3 == 0 else math.inf
    div2 = min_ops[i // 2] if i % 2 == 0 else math.inf
    add = min_ops[i - 1]

    previous = [i // 3, i // 2, i - 1]
    prev_ops = [div3, div2, add]
    best = prev_ops.index(min(prev_ops))
    return previous[best]

def optimal_sequence(n):
    min_ops = {}
    for i in range(1, n + 1):
        if i == 1:
            ops = 0
        else:
            best = best_previous(min_ops, i)
            ops = min_ops[best] + 1
        min_ops[i] = ops
    return backtrace(min_ops, n)

def backtrace(min_ops, n):
    sequence = []
    x = n
    while x > 1:
        sequence.append(x)
        x = best_previous(min_ops, x)
    sequence.append(1)
    return reversed(sequence)

input = sys.stdin.read()
n = int(input)
sequence = list(optimal_sequence(n))
print(len(sequence) - 1)
for x in sequence:
    print(x, end=' ')
