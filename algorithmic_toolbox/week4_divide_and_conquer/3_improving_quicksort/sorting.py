# Uses python3
import sys
import random


######################
# i = l + 1
# 5 3 4 6 8 5
#   ^
#   |
#  i,j
# Swap nothing happens
######################
# i = l + 2
# 5 3 4 6 8 5
#     ^
#     |
#    i,j
# Swap nothing happens
######################
# i = l + 3
# 5 3 4 6 8 5
#     ^ ^
#     | |
#     j i
# Greater nothing happens
######################
# i = l + 4
# 5 3 4 6 8 5
#     ^   ^
#     |   |
#     j   i
# Greater nothing happens
######################
# i = l + 4
# 5 3 4 6 8 5
# 5 3 4 5 8 6
#       ^   ^
#       |   |
#       j   i
# Equal swap
######################
# Termination
# i = l + 4
# 5 3 4 5 8 6
# 5 3 4 5 8 6
# ^     ^
# |     |
# l     j
# Swap l and j
######################
# With partiotion3
# 10 1 5 8 4 10 10 11  9 20 10 8
#  ^       ^     ^     ^
#  |       |     |     |
#  l       j     k     i
# Increment both
# 10 1 5 8 4 10 10 11  9 20 10 8
#  ^          ^     ^  ^
#  |          |     |  |
#  l          j     k  i
# Three way swap: a[i], a[j], a[k] = a[k], a[i], a[j]
# 10 1 5 8 4  9 10 10 11 20 10 8
#  ^          ^     ^  ^
#  |          |     |  |
#  l          j     k  i
# When they are equal
# 10 1 5 8 4  9 10 10 11 20 10 8
#  ^          ^     ^        ^
#  |          |     |        |
#  l          j     k        i
# Increment k
# 10 1 5 8 4  9 10 10 11 20 10 8
#  ^          ^        ^     ^
#  |          |        |     |
#  l          j        k     i
# Swap i, k
# 10 1 5 8 4  9 10 10 10 20 11 8
#  ^          ^        ^     ^
#  |          |        |     |
#  l          j        k     i
# Again, double increment + 3-way swap
# 10 1 5 8 4  9  8 10 10 10 11 20
#  ^             ^        ^    ^
#  |             |        |    |
#  l             j        k    i
# Termination, swap l and j
#  8 1 5 8 4  9 10 10 10 10 11 20
#  ^             ^        ^    ^
#  |             |        |    |
#  l             j        k    i




def partition3(a, l, r):
    x = a[l]
    # j points to the last that is > l
    # k points to the last that is == l
    j = k = l
    for i in range(l + 1, r + 1):
        if a[i] < x:
            # Increment both
            j += 1
            k += 1
            if j == k:
                # No need to triple swap
                a[i], a[k] = a[k], a[i]
            else:
                # Triple swap
                a[i], a[j], a[k] = a[k], a[i], a[j]
        elif a[i] == x:
            # Just increment k
            k += 1
            a[i], a[k] = a[k], a[i]

    a[l], a[j] = a[j], a[l]
    return j, k

def partition2(a, l, r):
    x = a[l]
    j = l
    for i in range(l + 1, r + 1):
        if a[i] <= x:
            j += 1
            a[i], a[j] = a[j], a[i]
    a[l], a[j] = a[j], a[l]
    return j


def randomized_quick_sort(a, l, r):
    if l >= r:
        return
    k = random.randint(l, r)
    a[l], a[k] = a[k], a[l]
    # m = partition2(a, l, r)
    # randomized_quick_sort(a, l, m - 1);
    # randomized_quick_sort(a, m + 1, r);
    #use partition3
    m1, m2 = partition3(a, l, r)
    randomized_quick_sort(a, l, m1 - 1);
    randomized_quick_sort(a, m2 + 1, r);


if __name__ == '__main__':
    input = sys.stdin.read()
    n, *a = list(map(int, input.split()))
    randomized_quick_sort(a, 0, n - 1)
    for x in a:
        print(x, end=' ')
