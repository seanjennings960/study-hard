# python3
import sys


def compute_min_refills(distance, tank, stops):
    num_stops = 0
    i = 0
    last = 0
    while last + tank < distance:
        while i < len(stops) and stops[i] - last <= tank:
            i += 1
        if i == 0 or stops[i - 1] == last:
            return -1
        last = stops[i - 1]
        num_stops += 1
    return num_stops




if __name__ == '__main__':
    d, m, _, *stops = map(int, sys.stdin.read().split())
    print(compute_min_refills(d, m, stops))
