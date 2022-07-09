# python3


class Database:
    def __init__(self, row_counts):
        self.row_counts = row_counts
        self.max_row_count = max(row_counts)
        n_tables = len(row_counts)
        self.ranks = [1] * n_tables
        self.parents = list(range(n_tables))

    def merge(self, src, dst):
        src_parent = self.get_parent(src)
        dst_parent = self.get_parent(dst)

        if src_parent == dst_parent:
            # Nothing to do, we are already merged.
            return False

        if self.ranks[src_parent] > self.ranks[dst_parent]:
            # Src is of greater rank, merge dst into src.
            self.parents[dst_parent] = src_parent
            # Just keep track of row_counts in parent.
            self.row_counts[src_parent] += self.row_counts[dst_parent]
            self.max_row_count = max(self.max_row_count,
                                      self.row_counts[src_parent])
        else:
            # The rank of the src_tree is smaller or equal to the
            # dst tree. Add src to dest
            self.parents[src_parent] = dst_parent
            self.row_counts[dst_parent] += self.row_counts[src_parent]
            self.max_row_count = max(self.max_row_count,
                                      self.row_counts[dst_parent])
            if self.ranks[src_parent] == self.ranks[dst_parent]:
                # If the ranks are the same, then the dst grows by 1.
                self.ranks[dst_parent] += 1
        return True

    def get_parent(self, table):
        # find parent and compress path
        p = self.parents[table]
        if table != p:
            # We are not yet at the root. Recursively call get_parent
            # until we reach the root
            self.parents[table] = self.get_parent(p)
        # The parent is now the root after path compression
        return self.parents[table]


def main():
    n_tables, n_queries = map(int, input().split())
    counts = list(map(int, input().split()))
    assert len(counts) == n_tables
    db = Database(counts)
    queries = []
    for i in range(n_queries):
        queries.append(map(int, input().split()))
    for dst, src in queries:
        db.merge(dst - 1, src - 1)
        print(db.max_row_count)


if __name__ == "__main__":
    main()
