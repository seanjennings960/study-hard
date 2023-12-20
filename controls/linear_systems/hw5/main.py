import numpy as np

def control(A, B):
    C = np.zeros((3, 3))
    C[:, 0] = B
    C[:, 1] = A @ B
    C[:, 2] = A @ A @ B
    return C

def problem1_1():
    A = np.array([
        [0, 1, 2],
        [0, 0, 3],
        [0, 0, -1]
    ])
    B = np.array([0, 1, 0])
    K = np.array([1, 2, 0])
    print(np.linalg.eigvals(A - np.outer(B, K)))

def problem1_2():
    A = np.array([
        [0, 1, 0],
        [-1, 2, 5],
        [1, -1, -3]
    ])
    B = np.array([1, -1, 1])
    C = control(A, B)
    print(C)
    print(np.linalg.det(C))
    eig = np.linalg.eigvals(A)
    char_poly = np.polynomial.Polynomial.fromroots(eig)
    print(char_poly)

    A_1 = np.array([
        [0, 1, 0],
        [0, 0, 1],
        [2, 0, -1]
    ])
    B_1 = np.array([0, 0, 1])
    C_1 = control(A_1, B_1)
    P = C_1 @ np.linalg.inv(C)
    print(P)
    assert np.all(np.isclose(A_1, P @ A @ np.linalg.inv(P)))
    assert np.all(np.isclose(B_1, P @ B))
    print("Det A", np.linalg.det(A))
    print("Det A_1", np.linalg.det(A_1))

    p = np.polynomial.Polynomial.fromroots(
        [-1, complex(-2, 1), complex(-2, -1)]
    )
    print(p)
    K_1 = np.array([7, 9, 4])
    K = K_1 @ P
    print(K)

    A_check = A - np.outer(B, K)
    print(np.linalg.eigvals(A_check))
    A_1_check = A_1 - np.outer(B_1, K_1)
    print(A_check)
    print(A_1_check)
    print("B K", np.outer(B, K))
    print("B' K'", np.outer(B_1, K_1))
    print(np.linalg.eigvals(A_1_check))
    print(np.linalg.det(A_check))
    print(np.linalg.det(A_1_check))

def problem1_3():
    A = np.eye(3)
    A[0, 0] = -1
    A[1, 1] = -1
    B = np.array([0, 1, 1])
    P = np.array([
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 0]
    ])
    P_2 = 1/2 * np.array([
        [-1, 1],
        [1, 1]
    ])
    A_11 = np.array([
        [-1, 0],
        [0, 1]
    ])
    B_1 = np.array([1, 1])
    print(P @ A @ np.linalg.inv(P))
    print(P @ B)
    A_prime = np.array([
        [0, 1],
        [1, 0]
    ])
    assert np.all(np.isclose(P_2 @ A_11 @ np.linalg.inv(P_2), A_prime))
    B_prime = np.array([0, 1])
    assert np.all(np.isclose(B_prime, P_2 @ B_1))
    print(np.linalg.eigvals([
        [-3, 0],
        [-2, 1]
    ]))
    print(np.linalg.eigvals([
        [0, 1],
        [-1, 2]
    ]))
    K = np.array([0, 0, -2])
    A_check = A + np.outer(B, K)
    print(A_check)
    print(np.linalg.eigvals(A_check))

def problem2_1():
    A_T = np.array([
        [0, 0, 1],
        [1, 0, 0],
        [0, 1, 0]
    ])
    print(np.linalg.eigvals(A_T))
    p = np.polynomial.Polynomial.fromroots(np.linalg.eigvals(A_T))
    print(p)
    p_design = np.polynomial.Polynomial.fromroots([-1, complex(-2, 1), complex(-2, -1)])
    print(p_design)
    D = np.array([
        [-5, 1, 0],
        [-9, 0, 1],
        [-5, 0, 0]
    ])
    print(np.linalg.eigvals(D))

def problem2_2():
    A = np.array([
        [0, 1],
        [10, 0]
    ])
    B = np.array([0, 1])
    C = np.array([1, 0])

    K = np.array([-14, -4])
    L = np.array([-4, -14])
    print(np.linalg.eigvals(A + np.outer(B, K)))
    print(np.linalg.eigvals(A + np.outer(L, C)))

def main():
    problem1_2()



if __name__ == "__main__":
    main()