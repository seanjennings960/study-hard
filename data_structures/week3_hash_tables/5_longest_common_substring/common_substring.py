# python3


import sys
from collections import namedtuple

Answer = namedtuple('answer_type', 'i j len')


def hash_prefixes(s, x, p):
    l_s = len(s)
    hash_array = [0]
    for c in s:
        hash_array.append(
            hash_array[-1] * x + ord(c) % p)
    return hash_array


class SubstringHash:
    # PRIMES = [1_000_000_007, 1_000_000_009]
    PRIMES = [1_000_000_007]
    MULTIPLIER = 12452

    def __init__(self, s):
        self._prefixes = {p: hash_prefixes(s, self.MULTIPLIER, p)
                          for p in self.PRIMES}
        self.s = s
        self.l_s = len(s)

    def generate_map(self, k):
        H = self._prefixes
        x_k = {p: 1 for p in self.PRIMES}
        for _ in range(k):
            for p in self.PRIMES:
                x_k[p] = (x_k[p] * self.MULTIPLIER) % p

        for i in range(self.l_s - k + 1):
            hash_ = tuple(
                (H[p][i + k] - x_k[p] * H[p][i]) % p
                for p in self.PRIMES)
            yield (hash_, i)

    def map(self, k):
        """
        Return a map containing all substring hashes of length k.

        Map a tuple of hashes to the index at which the substring
        starts.

        NOTE: a tuple of indexes should make it very improbable that
        we have collisions and avoid chaining.
        """
        return {hash_tup: i for hash_tup, i in self.generate_map(k)}

        # return [(H[i + k] - x_k * H[i]) % p
        #         for i in range(self.l_s - k + 1)]


        # arrays = [self._hash_array(k, p) for p in self.PRIMES]
        # return {hash_tup: i for (i, hash_tup) in enumerate(zip(*arrays))}


def longest_common_substring(s, t):
    s_hashes = SubstringHash(s)
    t_hashes = SubstringHash(t)
    # Initialize substring length k to be in the middle
    # of the shorter length, to start binary search.
    best_match = None

    lower = 0
    upper = min(len(s), len(t))
    k = upper // 2
    while upper >= lower and k > 0:
        new_matches = False
        t_k = t_hashes.map(k)

        for hash_tup, i in s_hashes.generate_map(k):
            if hash_tup in t_k:
                best_match = Answer(i, t_k[hash_tup], k)
                new_matches = True

        if new_matches:
            # We match so check larger substrings.
            lower = k + 1
        else:
            # No matches so decrease upper bound
            upper = k - 1
        k = (lower + upper) // 2
    # Since k can only increase after finding a new match, we can just return
    # the value at the end of the list.
    if best_match:
        return best_match
    else:
        return Answer(0, 0, 0)


def main():
    for data in sys.stdin.readlines():
        s, t = data.split()
        ans = longest_common_substring(s, t)
        print(ans.i, ans.j, ans.len)


if __name__ == '__main__':
    main()
