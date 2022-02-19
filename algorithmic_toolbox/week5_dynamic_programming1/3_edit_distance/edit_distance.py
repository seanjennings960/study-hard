# Uses python3


#########################
# s = edit
# t = distance
#   0  e  d  i  t
# 0 0->1->2->3->4
#   | \  \
# d 1  1  1->2->3
#   | \| \| \
# i 2  2  2  1->2
#   | \| \|  | \
# s 3  3  3  2  2
#   | \| \|  | \
# t 4  4  4  3  2
#   | \| \|  |  |
# a 5  5  5  4  3
#   | \| \|  |  |
# n 6  6  6  5  4
#   | \| \|  |  |
# c 7  7  7  6  5
#   | \  \|  |  |
# e 8  7->8  7  6
#
# ---------------
# e | d | i | - | t | - | - | - | -
# - | d | i | s | t | a | n | c | e



def edit_distance(s, t):
    m, n = len(s), len(t)
    dists = [[0] * (n + 1) for _ in range(m + 1)]
    # Initialize the first row and column, to be equal to the index.
    # This corresponds to only insertions/deletions.
    for i in range(m + 1):
        dists[i][0] = i
    for j in range(n + 1):
        dists[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            insert = dists[i][j - 1] + 1
            delete = dists[i - 1][j] + 1
            pair = dists[i - 1][j - 1]
            if s[i - 1] != t[j - 1]:
                pair += 1
            dists[i][j] = min(insert, delete, pair)
    return dists[-1][-1]


if __name__ == "__main__":
    print(edit_distance(input(), input()))
