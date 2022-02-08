# python3


def max_pairwise_product(numbers):
    max0 = max(numbers)
    numbers = numbers.copy()
    numbers.remove(max0)
    return max0 * max(numbers)


if __name__ == '__main__':
    input_n = int(input())
    input_numbers = [int(x) for x in input().split()]
    print(max_pairwise_product(input_numbers))
