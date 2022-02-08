def mean(x, y):
    return int((x + y) / 2)

def bin_search(low, high):
    while True:
        mid = mean(low, high)
        print('next:', mid)
        outcome = input('< or > ')
        if outcome.startswith('>'):
            low = mid + 1
        elif outcome.startswith('<'):
            high = mid - 1
        else:
            print('invalid input')
    print('done')


if __name__ == '__main__':
    bin_search(1, 2097151)
