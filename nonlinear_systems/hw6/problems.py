import numpy as np
import matplotlib.pyplot as plt

def problem_3():
    a = 1
    b = 2
    c = -5
    def G(s):
        return a / (s ** 2 - (c-1) * s - c - a * b)

    s = complex(0, 1)  * np.logspace(-3, 1)
    omega = np.imag(s)
    deriv = 2 * omega * (2 * omega**2 + 2 * c + 2 * a*b + (c - 1)**2)
    print(s.shape)
    G_on_imag = np.abs(G(s))
    print(G_on_imag.shape)
    plt.figure()
    # plt.semilogx(np.imag(s), G_on_imag)
    plt.semilogx(omega, deriv)
    plt.show()


    
    



def main():
    problem_3()

if __name__ == '__main__':
    main()