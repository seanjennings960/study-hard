# Uses python3
import sys

def get_change(m):
    coins = [10, 5, 1]
    current = 0

    num_coins = 0
    total = 0
    while total < m:
        if m - total < coins[current]:
            current += 1
            continue
        total += coins[current]
        num_coins += 1

    return num_coins

if __name__ == '__main__':
    m = int(sys.stdin.read())
    print(get_change(m))
