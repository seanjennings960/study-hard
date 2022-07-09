
class Query:
    def __init__(self, q):
        self.type = q[0]
        if self.type == 'check':
            self.index = int(q[1])
        else:
            self.name = q[1]


class HashMap:
    _PRIME = 1_000_000_007
    _MULTIPLIER = 263

    def __init__(self, n_buckets):
        self.chains = [[] for _ in range(n_buckets)]
        self.n_buckets = n_buckets

    def _hash_func(self, s):
        # Polynomial hash function taking in a string.
        out = 0
        for i in range(len(s) - 1, -1, -1):
            out = (out * self._MULTIPLIER + ord(s[i])) % self._PRIME
        return out % self.n_buckets

    def add(self, name):
        chain = self.chains[self._hash_func(name)]
        if name not in chain:
            # We insert at the beginning of the chain for some reason?
            # Perhaps related to a single linked list implementation...
            chain.insert(0, name)

    def del_(self, name):
        chain = self.chains[self._hash_func(name)]
        try:
            chain.remove(name)
        except ValueError:
            pass

    def find(self, name):
        return name in self.chains[self._hash_func(name)]

    def check(self, i):
        return self.chains[i]









def read_queries(n):
    queries = [input().split() for _ in range(n)]
    return [Query(q) for q in queries]


def process(m, queries):
    hash_map = HashMap(m)
    results = []
    for q in queries:
        if q.type == 'add':
            hash_map.add(q.name)
        elif q.type == 'del':
            hash_map.del_(q.name)
        elif q.type == 'find':
            found = 'yes' if hash_map.find(q.name) else 'no'
            results.append(found)
        elif q.type == 'check':
            chain = hash_map.check(q.index)
            if chain:
                results.append(' '.join(chain) + ' ')
            else:
                results.append('')
    return results





if __name__ == '__main__':
    m = int(input())
    n_queries = int(input())
    queries = read_queries(n_queries)
    responses = process(m, queries)
    for resp in responses:
        print(resp)

