from itertools import chain, filterfalse

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import inv, norm

##############################################################################
# Cubic Spline Interpolation
##############################################################################


def eval_local_spline(xeval,xi,xip,Mi,Mip,C,D):
    # Evaluates the local spline as defined in class
    # xip = x_{i+1}; xi = x_i
    # Mip = M_{i+1}; Mi = M_i

    hi = xip-xi
    yeval = (Mi*(xip-xeval)**3 +(xeval-xi)**3*Mip)/(6*hi) \
            + C*(xip-xeval) + D*(xeval-xi)
    return yeval


class CubicSpline:
    def __init__(self, xint, M, C, D):
        self.xint = xint
        self.Nint = xint.shape[0] - 1
        self.M = M
        self.C = C
        self.D = D

    def eval(self, xeval):
        M = self.M
        C = self.C
        D = self.D

        Neval = xeval.shape[0]
        yeval = np.zeros(Neval)

        for j in range(self.Nint):
            # find indices of xeval in interval (xint(jint),xint(jint+1))
            # let ind denote the indices in the intervals
            atmp = self.xint[j]
            btmp= self.xint[j+1]

            #   find indices of values of xeval in the interval
            ind= np.where((xeval >= atmp) & (xeval <= btmp))
            xloc = xeval[ind]
            #  print('atmp =', atmp)
            #  print('btmp =', btmp)
            #  print('ind =', ind)
            #  print('xloc =', xloc)
            #  return

            # evaluate the spline
            yloc = eval_local_spline(xloc,atmp,btmp,M[j],M[j+1],C[j],D[j])
            # print('yloc = ', yloc)
            # copy into yeval
            yeval[ind] = yloc

        return(yeval)

    @classmethod
    def from_natural_boundaries(cls, xint, yint):
        N = xint.shape[0] - 1

        # create the right  hand side for the linear system
        b = np.zeros(N+1)
        #  vector values
        h = np.zeros(N+1)
        for i in range(1,N):
            hi = xint[i]-xint[i-1]
            hip = xint[i+1] - xint[i]
            b[i] = (yint[i+1]-yint[i])/hip - (yint[i]-yint[i-1])/hi
            h[i-1] = hi
            h[i] = hip

        #  create matrix so you can solve for the M values
        # This is made by filling one row at a time
        A = np.zeros((N+1,N+1))
        A[0][0] = 1.0
        for j in range(1,N):
            A[j][j-1] = h[j-1]/6
            A[j][j] = (h[j]+h[j-1])/3
            A[j][j+1] = h[j]/6
        A[N][N] = 1

        M  = inv(A).dot(b)

        #  Create the linear coefficients
        C = np.zeros(N)
        D = np.zeros(N)
        for j in range(N):
            C[j] = yint[j]/h[j]-h[j]*M[j]/6
            D[j] = yint[j+1]/h[j]-h[j]*M[j+1]/6
        return cls(xint, M,C,D)

    @classmethod
    def from_clamped_boundaries(cls, xint, yint, yp_b):
        N = xint.shape[0] - 1

        #    create the right  hand side for the linear system
        b = np.zeros(N+1)
        #  vector values
        h = np.zeros(N+1)
        for i in range(1,N):
            hi = xint[i]-xint[i-1]
            hip = xint[i+1] - xint[i]
            b[i] = (yint[i+1]-yint[i])/hip - (yint[i]-yint[i-1])/hi
            h[i-1] = hi
            h[i] = hip
        b[0]  = -yp_b[0] +(yint[1]-yint[0])/h[0]
        b[N] = -yp_b[1] +(yint[N]-yint[N-1])/h[N-1]

        #  create matrix so you can solve for the M values
        # This is made by filling one row at a time
        A = np.zeros((N+1,N+1))
        A[0][0] = h[0]/3.
        A[0][1] = h[0]/6.
        for j in range(1,N):
            A[j][j-1] = h[j-1]/6
            A[j][j] = (h[j]+h[j-1])/3
            A[j][j+1] = h[j]/6
        A[N][N] = h[N-1]/3
        A[N][N-1] = h[N-1]/6

        M  = inv(A).dot(b)

        #  Create the linear coefficients
        C = np.zeros(N)
        D = np.zeros(N)
        for j in range(N):
            C[j] = yint[j]/h[j]-h[j]*M[j]/6
            D[j] = yint[j+1]/h[j]-h[j]*M[j+1]/6
        return cls(xint, M,C,D)


##############################################################################
# Lagrange Interpolation
##############################################################################


def _lagrange_basis(x, j):
    """Return the j-th Lagrange basis function for nodes x"""
    N = len(x)
    def l_j(x_in):
        prod = np.ones_like(x_in)
        for i in chain(range(j), range(j+1, N)):
            prod *= (x_in - x[i]) / (x[j] - x[i])
        return prod
    return l_j


def lagrange_polynomial(x, f):
    """
    Create a polynomial which interpolates between each point (x[i], f[i])
    """
    N = len(x)
    if len(f) != N:
        err = "x and f must be 1-dim vectors with same length."
        raise ValueError(err)
    l_basis = [_lagrange_basis(x, j) for j in range(len(x))]

    def p(x_in):
        # allow x_in to be a scalar or array of length M.
        # the list comprehension is stored as either
        # a (N,) array or (N, M). Sum over the first axis
        # in either case.
        return np.sum([l_basis[j](x_in) * f[j]
                       for j in range(N)], axis=0)
    return Polynomial(p)


class Polynomial:
    def __init__(self, p):
        self.p = p

    def eval(self, x_eval):
        return self.p(x_eval)


##############################################################################
# Hermite Interpolation
##############################################################################

def range_minus(N, excluded):
    return filterfalse(lambda x: x in excluded, range(0, N))


def _lagrange_deriv(x, j):
    N = len(x)
    def ld_j(x_in):
        numerator = np.zeros_like(x_in)
        for k in range_minus(N, [j]):
            numerator += np.prod(
                [x_in - x[i] for i in range_minus(N, [j, k])],
                axis=0
            )
        denom = np.prod(
            [x[j] - x[i] for i in range_minus(N, [j])],
            axis=0
        )
        return numerator / denom
    return ld_j


def _hermite_basis(x, j):
    lj = _lagrange_basis(x, j)
    ld_j = _lagrange_deriv(x, j)

    def hj(x_in):
        return (1 - 2 * ld_j(x[j]) * (x_in - x[j])) * lj(x_in)**2

    def kj(x_in):
        return (x_in - x[j]) * lj(x_in)**2

    return hj, kj



def create_hermite_polynomial(x, y, z):
    """Create a hermite polynomial from given datapoints (y=f(x), z=f'(x))"""
    N = len(x)
    if len(y) != N or len(z) != N:
        raise ValueError("x, y, and z must all have same dimensions.")

    hk_basis = [_hermite_basis(x, j) for j in range(N)]

    def p(x_in):
        return np.sum(
            [y[i] * h_i(x_in) + z[i] * k_i(x_in)
             for i, (h_i, k_i) in enumerate(hk_basis)],
            axis=0
        )
    return Polynomial(p)


##############################################################################
# Chebychev Nodes
##############################################################################


# def create_chebychev_nodes(a, b, Nint):
#     # create chebychev nodes
#     xint = np.zeros(Nint+1)
#     for j in range(1,Nint+2):
#         xint[j-1] = np.cos(np.pi*(2*j-1)/(2*(Nint+1)))
#         # scale  for the interval
#         m = (b-a)/2
#         c = (a+b)/2
#         xint = m*xint+c
#         xint = xint[::-1]
#     return xint

def scale(x, c, d):
    a = x[0]
    b = x[-1]
    alpha = (d - c) / (b - a)
    beta = (b * c - a * d) / (b - a)
    return alpha * x + beta


def create_chebychev_nodes(a, b, n_points):
    js = np.arange(0, n_points)
    x = np.cos((2 * js + 1) * np.pi / (2 * n_points))
    # Flip direction so x is increasing.
    x = x[::-1]
    return scale(x, a, b)



##############################################################################
# Driver Code
##############################################################################



def plot_interpolation(N_intervals, *, chebychev=False, N_eval=1000):

    f = lambda x: 1 / (1 + x**2)
    df_dx = lambda x: -2 * x / (1 + x**2)**2

    interval = np.array([-5, 5])
    if chebychev:
        x_nodes = create_chebychev_nodes(*interval, N_intervals)
    else:
        x_nodes = np.linspace(*interval, N_intervals)
    y = f(x_nodes)
    dy_bound = df_dx(interval)

    interpolants = {
        "Lagrange": lagrange_polynomial(x_nodes, y),
        "Hermite": create_hermite_polynomial(x_nodes, y, df_dx(x_nodes)),
        "Cubic Spline -- Natural Boundary":
            CubicSpline.from_natural_boundaries(x_nodes, y),
        "Cubic Spline -- Clamped Boundary":
            CubicSpline.from_clamped_boundaries(x_nodes, y, dy_bound),
    }

    x = np.linspace(*interval, N_eval)
    f_eval = f(x)

    fig, axes = plt.subplots(2, 1)
    # Plot of Interpolants
    ax = axes[0]
    ax.plot(x, f_eval, "k-", label="exact")
    ax.plot(x_nodes, y, "ko", label="Interpolation nodes")

    for method, interpolant in interpolants.items():
        y_interp = interpolant.eval(x)
        ax.plot(x, y_interp, "--", label=f"interpolated ({method})")

    ax.legend()
    ax.set_title("Interpolated versus exact evaluation | f(x) = 1/(1 + x^2)")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x) / f_interpolated(x)")

    # Plot of Error
    ax = axes[1]
    for method, interpolant in interpolants.items():
        y_interp = interpolant.eval(x)
        err = abs(f_eval - y_interp)
        ax.semilogy(x, err, "--", label=f"{method} | ||err|| = {norm(err):.3f}")
    ax.legend()
    ax.set_title("Error ()")
    ax.set_xlabel("x")
    ax.set_ylabel("|f(x) - f_interp(x)|")

    return fig


def main():
    # for N in [5, 10, 15, 20]:
    for N in [5]:
        for chebychev in [False, True]:
            plot_interpolation(N, chebychev=chebychev)
            plt.show()




if __name__ == "__main__":
    main()
