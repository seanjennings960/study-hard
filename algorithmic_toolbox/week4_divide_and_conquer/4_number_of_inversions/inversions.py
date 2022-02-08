# Uses python3
import sys

def get_number_of_inversions(a, b, left, right):
    number_of_inversions = 0
    if right - left <= 1:
        return number_of_inversions
    ave = (left + right) // 2
    number_of_inversions += get_number_of_inversions(a, b, left, ave)
    number_of_inversions += get_number_of_inversions(a, b, ave, right)
    #write your code here
    i = left
    j = ave
    for k in range(left, right):
        if i >= ave:
            # We've taken everything from the left, so take
            # the rest from the right. No inversions.
            b[k] = a[j]
            j += 1
        elif j >= right:
            # We've taken everything from the right, so take
            # The rest from the left. Inversions have already
            # been counted.
            b[k] = a[i]
            i += 1
        elif a[i] > a[j]:
            # Take from the higher array, so we have
            # an inversion between each pair [(i, j)..(ave - 1, j)]
            number_of_inversions += (ave - i)
            b[k] = a[j]
            j += 1
        else:
            # Continue taking from the left side.
            b[k] = a[i]
            i += 1

    # Copy over from our intermediate array.
    a[left:right] = b[left:right]

    return number_of_inversions

if __name__ == '__main__':
    input = sys.stdin.read()
    n, *a = list(map(int, input.split()))
    b = n * [0]
    print(get_number_of_inversions(a, b, 0, len(a)))
