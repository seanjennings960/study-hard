import numpy as np


def inner(a, b):
    return np.dot(a, b.conj())


def gram_schmidt(w):
    # Given a set of `m` (linearly independent) vectors in `R^n`,
    # find a set of orthogonal vectors with the same span.
    # The input w is a 2D array of shape `(m, n)`, and the
    # output has the same shape.
    v = np.zeros_like(w)
    for i in range(v.shape[0]):
        v[i] = w[i]
        for j in range(i):
            print((i, j))
            print(v[i])
            print("Inner:", inner(w[i], v[j]))
            print("norm:", inner(v[j], v[j]))
            if np.isclose(inner(v[j], v[j]), 0):
                continue
            v[i] -= inner(w[i], v[j]) / inner(v[j], v[j]) * v[j]
        print(f"Final({i}:", v[i])
    return v


def main():
    v = np.array([
        [1, 0, 1],
        [0, 1, 1],
        [1, 3, 3]
    ], dtype=np.float64)
    print("v:")
    print(v)
    print(gram_schmidt(v))
    print("v:")
    v = np.array([
        [1, 0, complex(0, 1)],
        [1, 2, 1],
        [1, 0, 0],
        [complex(0, 1), 0, 0],
        [0, 1, 0],
        [0, complex(0, 1), 0],
        [0, 0, 1],
        [0, 0, complex(0, 1)],
    ])
    # v = np.empty((6, 3), dtype=np.complex128)
    # v.real = np.array([
    #     [1, 0, 0],
    #     [1, 2, 1],
    #     [1, 0, 0],
    #     [0, 0, 0],
    #     [0, 1, 0],
    #     [0, 0, 0]
    # ])
    # v.imag = np.array([
    #     [0, 0, 1],
    #     [0, 0, 0],
    #     [0, 0, 0],
    #     [1, 0, 0],
    #     [0, 0, 0],
    #     [0, 1, 0],

    # ])
    print("v:")
    print(v)
    w = gram_schmidt(v)
    print(np.round(w, 2))
    for i in range(w.shape[0]):
        for j in range(i):
            if np.isclose(inner(w[i], w[j]), 0):
                continue
            print((i,j))
            print("w[i]:", w[i])
            print("w[j]:", w[j])
            print("Inner:", inner(w[i], w[j]))



if __name__ == "__main__":
    main()
