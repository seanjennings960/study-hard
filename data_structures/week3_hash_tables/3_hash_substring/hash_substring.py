# python3

def read_input():
    return (input().rstrip(), input().rstrip())

def print_occurrences(output):
    print(' '.join(map(str, output)))


PRIME = 1_000_000_007
PRIME2 = 1_000_000_009
MULTIPLIER = 263


def hash_func(s, x, p):
    # Polynomial hash function taking in a string.
    out = 0
    for i in range(len(s)):
        out = (out * x + ord(s[i])) % p
    return out




def precompute_hashes(text, pattern, x, p):
    l_p = len(pattern)

    # Initialize first value of hash array using the full hash function,
    # to start the recursive formula
    H = [hash_func(text[:l_p], x, p)]
    # Precompute x ** p so that we don't include |P| inside text loop.
    x_p = 1
    for _ in range(l_p):
        x_p = (x_p * x) % p

    for i in range(len(text) - l_p):
        next_h = (x * H[i] + ord(text[i + l_p])
                  - x_p * ord(text[i])) % p
        H.append(next_h)
    return H


# def get_equal(a, b):
#     print('actually doing full check')
#     return a == b


def get_occurrences(pattern, text):
    l_p = len(pattern)

    hash_array = precompute_hashes(text, pattern, MULTIPLIER, PRIME)
    hash_array2 = precompute_hashes(text, pattern, MULTIPLIER, PRIME2)

    pattern_hash = hash_func(pattern, MULTIPLIER, PRIME)
    pattern_hash2 = hash_func(pattern, MULTIPLIER, PRIME2)

    return [i for i in range(len(text) - l_p + 1)
            if pattern_hash == hash_array[i] and pattern_hash2 == hash_array2[i]]
    # if pattern_hash == hash_array[i] and get_equal(text[i:i+l_p],
    #                                                pattern)]


if __name__ == '__main__':
    print_occurrences(get_occurrences(*read_input()))
