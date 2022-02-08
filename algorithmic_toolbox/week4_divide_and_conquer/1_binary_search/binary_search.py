# Uses python3
import sys

def binary_search(a, x):
    left, right = 0, len(a)
    # write your code here
    mid = int((left + right) / 2)
    # print('lrmx', left, right, mid, x)
    if right == 0:
        return -1
    elif a[mid] == x:
        # print('return:', mid)
        return mid
    elif a[mid] > x:
        return binary_search(a[:mid], x)
    else:
        # print('upper search at:', mid)
        output = binary_search(a[mid + 1:], x)
        return -1 if output == -1 else mid + output + 1


def linear_search(a, x):
    for i in range(len(a)):
        if a[i] == x:
            return i
    return -1

if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n = data[0]
    a = data[1 : n + 1]
    for x in data[n + 2:]:
        # replace with the call to binary_search when implemented
        print(binary_search(a, x), end = ' ')
