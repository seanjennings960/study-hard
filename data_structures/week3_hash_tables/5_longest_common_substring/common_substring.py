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
    PRIMES = [1_000_000_007, 1_000_000_009]
    MULTIPLIER = 12452

    def __init__(self, s):
        self._prefixes = {p: hash_prefixes(s, self.MULTIPLIER, p)
                          for p in self.PRIMES}
        self.s = s
        self.l_s = len(s)

    def _hash_array(self, k, p):
        H = self._prefixes[p]
        x_k = 1
        for _ in range(k):
            x_k = (x_k * self.MULTIPLIER) % p

        return [(H[i + k] - x_k * H[i]) % p
                for i in range(self.l_s - k + 1)]

    def map(self, k):
        """
        Return a map containing all substring hashes of length k.

        Map a tuple of hashes to the index at which the substring
        starts.

        NOTE: a tuple of indexes should make it very improbable that
        we have collisions and avoid chaining.
        """
        arrays = [self._hash_array(k, p) for p in self.PRIMES]
        return {hash_tup: i for (i, hash_tup) in enumerate(zip(*arrays))}


def longest_common_substring(s, t):
    s_hashes = SubstringHash(s)
    t_hashes = SubstringHash(t)
    # Initialize substring length k to be in the middle
    # of the shorter length, to start binary search.
    matches = []

    lower = 0
    upper = min(len(s), len(t))
    k = upper // 2
    while upper >= lower and k > 0:
        new_matches = False
        s_k = s_hashes.map(k)
        t_k = t_hashes.map(k)

        for hash_tup in s_k.keys():
            if hash_tup in t_k:
                matches.append(
                    Answer(s_k[hash_tup], t_k[hash_tup], k))
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
    if matches:
        return matches[-1]
    else:
        return Answer(0, 0, 0)


def main():
    for data in sys.stdin.readlines():
        s, t = data.split()
        ans = longest_common_substring(s, t)
        print(ans.i, ans.j, ans.len)


if __name__ == '__main__':
    main()
