# python3

def hash_func(s, x, p):
    # Polynomial hash function taking in a string.
    out = 0
    for i in range(len(s)):
        out = (out * x + ord(s[i])) % p
    return out


class Solver:
    PRIME_1 = int(1e9 + 7)
    PRIME_2 = int(1e9 + 9)
    MULTIPLIER = 12344

    def __init__(self, s):
        self.s = s
        self._hash_array_1 = self._precompute_hashes(s, self.PRIME_1)
        self._hash_array_2 = self._precompute_hashes(s, self.PRIME_2)
        self._xs1 = self._precompute_xs(self.PRIME_1, len(s))
        self._xs2 = self._precompute_xs(self.PRIME_2, len(s))

    def _precompute_xs(self, p, l_s):
        xs = [1]
        for i in range(l_s):
            xs.append((xs[-1] * self.MULTIPLIER) % p)
        return xs

    def _precompute_hashes(self, s, p):
        hashes = [0]
        total = 0
        for i in range(len(s)):
            total = (total * self.MULTIPLIER + ord(s[i])) % p
            hashes.append(total)
        return hashes

    def _substring_hash(self, a, l, mod):
        if mod == 1:
            hashes, p = self._hash_array_1, self.PRIME_1
            x_l = self._xs1[l]
        else:
            hashes, p = self._hash_array_2, self.PRIME_2
            x_l = self._xs2[l]
        return (hashes[a + l] - x_l * hashes[a]) % p

    def ask(self, a, b, l):
        h_a1, h_a2 = [self._substring_hash(a, l, m) for m in [1, 2]]
        h_b1, h_b2 = [self._substring_hash(b, l, m) for m in [1, 2]]
        return h_a1 == h_b1 and h_a2 == h_b2


if __name__ == '__main__':
    s = input()
    q = int(input())
    solver = Solver(s)
    queries = []
    for i in range(q):
        queries.append(map(int, input().split()))
    for a, b, l in queries:
        print("Yes" if solver.ask(a, b, l) else "No")
