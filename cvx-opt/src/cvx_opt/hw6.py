import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import cvx_opt.functions as funcs


def std_basis(n, i):
    # Return i-th standard basis vector.
    out = np.zeros(n)
    out[i] = 1
    return out

def _grad_central_diff(f, x0, h):
    n = x0.shape[0]
    return np.array([
        (f(x0 + h * std_basis(n, i)) - f(x0 - h * std_basis(n, i))) / (2*h)
        for i in range(n)
    ])
    
def _grad_finite_diff(f, x0, h):
    n = x0.shape[0]
    f0 = f(x0)
    return np.array([
        (f(x0 + h * std_basis(n, i)) - f0) / h
        for i in range(n)
    ])
    

METHODS = {
    'central': _grad_central_diff,
    'finite_diff': _grad_finite_diff,
}
    

def grad(f, x0, h, method=None):
    if method not in METHODS:
        raise ValueError(f"Unknown method: '{method}'. Must be one of {METHODS.keys()}")
    return METHODS[method](f, x0, h)
    

@dataclass
class ErrorInfo:
    # Stepsizes
    h: np.ndarray
    x0: np.ndarray
    # RMS Error in numeric versus
    # ||grad_numeric(f, x0, h) - grad_analytic(f, x0)||_2
    errors_by_method: dict


def test_gradient(f, grad_f, x0):
    # Check whether that the given analytic gradient grad_f is 
    # close to the gradient computed numerically from f at a given
    # point x0.
    h = np.logspace(0, -15, 31)
    all_errors = {}
    for method in METHODS.keys():
        errors = np.full_like(h, np.nan)
        for i, h_i in enumerate(h):
            numeric_grad = grad(f, x0, h_i, method)
            analytic_grad = grad_f(x0)
            errors[i] = np.linalg.norm(numeric_grad - analytic_grad)
        all_errors[method] = errors

    
    return ErrorInfo(h=h, x0=x0, errors_by_method=all_errors)


def plot_errors(info, func_name, save_dir):
    fig = plt.figure()
    for method, error in info.errors_by_method.items():
        # if method != "central":
        #     continue
        plt.loglog(info.h, error, '-o', label=method)
    plt.legend()
    plt.xlabel("h (stepsize)")
    plt.ylabel("error")
    plt.title(f"Numeric gradient error for {func_name} \n at {np.round(info.x0, 2)}")
    if save_dir is not None:
        x0_str = np.round(info.x0, 2)[0]
        filename = f"{x0_str}_{func_name.replace(' ', '_')}.png"
        fig.savefig(save_dir / filename)
        
        
        

def problem_1(save_dir=None):
    np.random.seed(0)
    N = 10
    P = 5
    X = np.random.uniform(0, 10, (N, P))
    y = np.where(np.random.uniform(0, 1, N) < 0.5, -1, 1)
    w0_log = np.random.uniform(-5, 5, P)


    x0_1d = np.array([5])
    for x0, func in [
        (x0_1d, funcs.Linear(21.0, 5.)),
        (x0_1d, funcs.Quadratic(5, 1, 20)),
        (x0_1d, funcs.Cubic([5, 4, 3, 2])),
        (w0_log, funcs.LogLikelihoodLogistic(X, y)),
        (np.zeros(P), funcs.LogLikelihoodLogistic(X, y)),
        (x0_1d, funcs.IncorrectLinear(21.0, 5.)),
    ]:
        e = test_gradient(func.f, func.grad, x0)
        plot_errors(e, str(func), save_dir)


###############################################################
# Gradient Descent
###############################################################

@dataclass
class SolverResult:
    solution: np.ndarray
    converged: bool
    steps: np.ndarray

    
def gradient_descent(f, grad, x0, stepsize, tol=1e-6, maxiters=int(1e3)):
    
    N = x0.shape[0]
    steps = np.full((maxiters, N), np.nan)
    
    f0 = f(x0)
    
    for i in range(maxiters):
        steps[i] = x0
        
        # Move in the descent direction
        x1 = x0 - grad(x0) * stepsize
        f1 = f(x1)
        
        if abs(f1 - f0) < tol:
            # Converged successfully
            return SolverResult(x1, True, steps[:i+1])
        # Update variables for next loop iteration
        f0 = f1
        x0 = x1
    # maxiters was exceeded without reaching tolerance
    return SolverResult(x0, False, steps)
    

###############################################################
# Gradient Descent w/linesearch
###############################################################
        
@dataclass
class SolverResultSearch(SolverResult):
    t_history: np.ndarray

def descent_with_search(f, grad, x0, c=1e-4, rho=0.9, t0=1e-3, tol=1e-6, maxiters=int(1e3)):
    N = x0.shape[0]
    steps = np.full((maxiters + 1, N ), np.nan)
    t_history = np.full((maxiters + 1), np.nan)

    f0 = f(x0)
    steps[0] = x0

    t = t0
    t_history[0] = t
    for i in range(maxiters):

        p = -grad(x0)
        norm2_p = np.vdot(p, p)
        count = 0
        while f(x0 + t * p) > f0 - c * t * norm2_p:
            t *= rho
            count += 1
        x1 = x0 + t * p
        f1 = f(x1)
        steps[i+1] = x1
        t_history[i+1] = t
        # print("x0:", x0)
        # print("x1:", x1)
        # print("f0:", f0)
        # print("f1:", f1)
        # print("f1 - f0:", f1 - f0)

        if abs(f1 - f0) < tol:
            # print("f0:", f0)
            # print("f1 - f0:", f1 - f0)
            return SolverResultSearch(x1, True, steps[:i+2], t_history[:i+2])

        f0 = f1
        x0 = x1
        if count == 0:
            print("Exited on first step.")
            t*=100
        else:
            t *= 2
    return SolverResultSearch(x0, False, steps, t_history)
        
        
def spectral_norm(A):
    return np.linalg.svd(A, compute_uv=False)[0]

def problem_2_3(save_dir):
    np.random.seed(0)
    M = 100
    N = 50
    A = np.random.uniform(0, 10, (M,N))
    b = np.ones(M)
    # x_star = np.linalg.inv(A.T @ A) @ A.T @ b
    x_star, _, rank, _ = np.linalg.lstsq(A, b)

    def f(x):
        return 1/2 * np.linalg.norm(A @ x - b)

    def grad_f(x):
        return A.T @ (A @ x - b)


    x0 = np.zeros(N)
    stepsize = 1 / spectral_norm(A)**2
    res = gradient_descent(f, grad_f, x0, stepsize, tol=1e-10, maxiters=10000)
    err_gd = np.linalg.norm(res.steps - x_star, axis=1)
    print("Gradient Descent converged:", res.converged)


    x0 = np.zeros(N)
    stepsize = 1 / spectral_norm(A)**2
    res = descent_with_search(f, grad_f, x0, tol=1e-10, maxiters=10000)
    err_search = np.linalg.norm(res.steps - x_star, axis=1)
    print(res.converged)

    fig = plt.figure()
    plt.semilogy(err_gd, label="Gradient Descent")
    plt.semilogy(err_search, label="Gradient Descent with linesearch")
    plt.title("Error vs gradient descent iteration on f(x) = 1/2||Ax-b||^2")
    plt.xlabel("Iteration number")
    plt.ylabel("Error ||x_k - x^*||_2")
    plt.legend()
    fig.savefig(save_dir / "gradient_descent_results.png")

    

        

                    