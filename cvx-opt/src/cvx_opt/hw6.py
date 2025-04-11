from typing import Optional, Tuple
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
import cvx_opt.functions as funcs
from pathlib import Path
from scipy.optimize import fmin

DATA_DIR = Path("/Users/sean/code/study-hard/cvx-opt/data")


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
    steps: Optional[np.ndarray]
    costs: np.ndarray

    def plot(self, log=False, loglog=False):
        plt.figure()
        if loglog:
            plt.loglog(self.costs)
        elif log:
            plt.semilogy(self.costs)
        else:
            plt.plot(self.costs)
        plt.xlabel("Solver Iteration (k)")
        plt.ylabel("Function cost f(x) + g(x)")

    def plot_solution(self, N_features, title=None):
        if self.steps is None:
            raise ValueError("Full solution history was not saved!")
        plt.figure()
        plt.plot(self.steps[:, :N_features])
        plt.legend([f"feature {i}" for i in range(N_features)])
        plt.xlabel("Iteration")
        plt.ylabel("Cost Evaluation")
        if title is not None:
            plt.title(title)

    def __repr__(self):
        return f"""SolverResult:
    Converged={self.converged}
    iterations={len(self.costs) - 1}
    function_eval={self.costs[-1]}
"""

    
def gradient_descent(f, grad, x0, stepsize, tol=1e-6, maxiters=int(1e3)):
    
    N = x0.shape[0]
    steps = np.full((maxiters, N), np.nan)
    costs = np.full(maxiters, np.nan)

    for i in range(maxiters):
        steps[i] = x0
        costs[i] = f(x0)
        
        # Move in the descent direction
        x1 = x0 - grad(x0) * stepsize
        
        if np.linalg.norm(x1 - x0) < tol:
            # Converged successfully
            return SolverResult(x1, True, steps[:i+1], costs[:i+1])
        # Update variables for next loop iteration
        x0 = x1
    # maxiters was exceeded without reaching tolerance
    return SolverResult(x0, False, steps, costs)
    

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

    

        
def shuffle(X):
    order = np.random.permutation(X.shape[0])
    return X[order]



@dataclass
class Dataset:
    X: np.ndarray
    y: np.ndarray
    N_train: int

    @property
    def training(self) -> Tuple[np.ndarray, np.ndarray]:
        # Returns training set (X, y) as tuple
        return self.X[:self.N_train], self.y[:self.N_train]
    
    @property
    def testing(self) -> Tuple[np.ndarray, np.ndarray]:
        # Returns testing set (X, y) as tuple
        return self.X[self.N_train:], self.y[self.N_train:]



    # ell_train = LL(X[:N_train], y[:N_train])
    # ell_test = LL(X[N_train:], y[N_train:])

    # class_train = classify(ell_train, res.solution)
    # misclass_train = np.sum(~np.isclose(class_train, y[:N_train]))
    # print(misclass_train / N_train)

    # class_train = classify(ell_train, res.solution)
    # print(class_train.shape)
    # misclass_train = np.sum(class_train != y[:N_train])
    # print(misclass_train / N_train)

def load_data(N_train=3065) -> Dataset:
    data = np.loadtxt(DATA_DIR / 'spam.data', delimiter=" ")
    X, y = data[:, :-1], data[:, -1]
    # Remap 0 to -1
    y[y==0] = -1
    X = np.log(X + 0.1)
    return Dataset(X=X, y=y, N_train=N_train)


# def train(X, y):
# 
#     def train(X, y):
#         w0 = np.zeros(X.shape[1])
#         ell = funcs.LogLikelihoodLogistic(X, y)
#         # return descent_with_search(ell.f, ell.grad, w0, t0=1e-2, maxiters=10000)
#         result = gradient_descent(ell.f, ell.grad, w0, stepsize=1e-5, maxiters=100000)
#         result.f = ell.f
#         return result
# 
# def problem_4():
#     # Load the dataset
#     dataset = load_data()
# 


####################################################################################
# Solving Spam problem in various ways
####################################################################################
##
def gradient_descent_cost(cost, x0, stepsize, **kwargs):
    return gradient_descent(cost.f, cost.grad, x0, stepsize, **kwargs)

class Model:
    def __init__(self, cost, solver=gradient_descent_cost, solver_options=None):
        self.cost = cost
        self.solver = solver
        self.solver_options = {} if solver_options is None else solver_options
        
        self.ell_train = None
        self.ell_test = None
        
        self.result = None
        self.w = None


    def train(self, dataset):
        X, y = dataset.training
        
        x0 = np.zeros(X.shape[1])
        
        self.ell_train = self.cost(X, y)
        self.result = self.solver(self.ell_train, x0, **self.solver_options)


        def cost_eval(x):
            # well... this is pretty hacky and doesn't actually work properly for some reason
            ns_cost = self.solver_options.get("nonsmooth_cost")
            if ns_cost is not None:
                return self.ell_train.f(x) + ns_cost.g(x)
            else:
                return self.ell_train.f(x)

        self.result.f = cost_eval
        self.w = self.result.solution
        return self.result

    def validate(self, dataset):
        X, y = dataset.testing
        self.ell_test = self.cost(X, y)

        return self.ell_test.f(self.w)
        
    def classification_rate(self, dataset, training=False):
        ell = self.ell_train if training else self.ell_test
        classes = ell.classify(self.w)
    
        y = (dataset.training if training else dataset.testing)[1]
        N_training = len(y)
        
        num_correct = np.sum(np.isclose(classes, y))
        return num_correct / N_training



# Proximal Gradient Descent Algorithm


class NonsmoothCost:
    """
    A (potentially) nonsmooth cost function.
    
    prox_g(t, y) = argmin_x t * g(x) - ||x-y||^2

    computable in closed form. This is implemented in prox method
    """

    def g(self, x):
        return self.g(x) + self.h(x)

    def prox(self, t, y):
        raise NotImplementedError


class NonsmoothIdentity:
    def __init__(self):
        pass
        
    def g(self, x):
        return 0

    def prox(self, t, y):
        return y

def prox_grad_operator(grad, prox, t):
    def p_t(y):
        return prox(t, y - t * grad(y))
    return p_t
    
def prox_gradient_descent(cost, x0, nonsmooth_cost=None, stepsize=1e-5, maxiters=int(1e5), tol=1e-5, full_history=True):
    if nonsmooth_cost is None:
        nonsmooth_cost = NonsmoothIdentity()
    
    prox_grad = prox_grad_operator(cost.grad, nonsmooth_cost.prox, stepsize)
    
    t0 = 1
    # Not used on first iteration
    x1 = None
    t1 = None

    N = x0.shape[0]
    cost_history = np.full(maxiters+1, np.nan)
    
    if full_history:
        steps = np.full((maxiters+1, N), np.nan)
        steps[0] = x0
    else:
        steps = None
    cost_history[0] = cost.f(x0) + nonsmooth_cost.g(x0)

    for k in range(maxiters):

        if k == 0:
            y = x0
        else:
            y = x1 + (t0 - 1) / t1 * (x1 - x0)
            # Save old x0 now it has been used.
            x0 = x1
            t0 = t1

        
        # Run proximal gradient operator
        x1 = prox_grad(y)
        t1 = (1 + np.sqrt(1 + 4 * t0**2))/2

        # Save history
        if full_history:
            steps[k + 1] = x1
        cost_history[k + 1] = cost.f(x1) + nonsmooth_cost.g(x1)

        if np.linalg.norm(x1 - x0) < tol:
            if full_history:
                steps = steps[:k+2]
            # Convergence
            return SolverResult(x1, True, steps, cost_history[:k+2])

    return SolverResult(x1, False, steps, cost_history)


def nelder_mead(cost, x0, **kwargs):
    """Model-compatible solver interface to scipy.optimize.fmin's Nelder-Mead implementation."""
    solution, _, _, _, status, steps = fmin(cost.f, x0, full_output=True, retall=True, **kwargs)
    costs = np.array([cost.f(x_i) for x_i in steps])
    result = SolverResult(solution, status==0, np.array(steps), costs)
    result.f = cost.f
    return result

# This is is a simple "zero" cost function since this is a required argument to prox_gradient_descent
class ZeroCost:
    def __init__(self):
        pass
        
    def f(self, x):
        return 0
        
    def grad(self, x):
        return np.zeros(x.shape[0], dtype=float)
    
    



FeatureNames = [
    'make', 'address', 'all', '3d', 'our', 'over', 'remove',
    'internet', 'order', 'mail', 'receive', 'will', 'people',
    'report', 'addresses', 'free', 'business', 'email', 'you',
    'credit', 'your', 'font', '000', 'money', 'hp', 'hpl', 'george',
    '650', 'lab', 'labs', 'telnet', '857', 'data', '415', '85',
    'technology', '1999', 'parts', 'pm', 'direct', 'cs', 'meeting',
    'original', 'project', 're', 'edu', 'table', 'conference', ';',
    '(', '[', '!', '$', '#','Avg capital letter',
    "Max capital letter", "Total capital letter"
]


def plot_features(w):
    posInd = (w>0)
    pos = np.argwhere( posInd.ravel() ).ravel()
    neg = np.argwhere( ~posInd.ravel() ).ravel()
    plt.stem(pos,w[posInd],linefmt='C0-',label='Positive coefficient (SPAM)',
        basefmt='')
    plt.stem(neg,-w[~posInd],linefmt='C1-',markerfmt='C1x',
        label='Negative coefficient (legit)',
        basefmt='')
    plt.legend()
    # Interesting features
    interesting = np.nonzero( (np.abs(w)>0.6).ravel() )[0]
    lbl=[] # one way to do it:
    [lbl.append(FeatureNames[int(i)]) for i in interesting]
    plt.xticks( interesting, labels=lbl )
    plt.xticks(rotation=90)
    plt.show()