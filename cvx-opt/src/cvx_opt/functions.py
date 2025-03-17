import numpy as np
from dataclasses import dataclass


@dataclass
class Linear:
    a: float
    b: float

    def f(self, x):
        return self.a * x + self.b

    def grad(self, x):
        return self.a

@dataclass
class IncorrectLinear:
    a: float
    b: float

    def f(self, x):
        return self.a * x + self.b

    def grad(self, x):
        return self.a + 1

@dataclass
class Affine:
    A: np.ndarray
    b: np.ndarray
    
    def f(self, x):
        return self.A @ x + self.b
        
    def grad(self, x):
        return self.A

@dataclass
class Quadratic:
    a: float
    b: float
    c: float 
    def f(self, x):
        return self.a * x**2 + self.b * x + self.c

    def grad(self, x):
        return 2 * self.a * x + self.b

@dataclass
class Cubic:
    c: np.ndarray
    
    def __init__(self, c):
        self.c = np.asarray(c)
        assert self.c.shape[0] == 4
        
    def f(self, x):
        return np.vdot(self.c, np.r_[x**3, x**2, x, 1])

    def grad(self, x):
        return np.vdot(self.c[:-1], np.r_[3 * x**2, 2*x, 1])


def sigmoid(a):
    # print(a)
    return 1 / (1 + np.exp(-a))
    
class LogLikelihoodLogistic:
    X: np.ndarray  # shape NxP where N is number of data points
    y: np.ndarray # shape N vector of labels

    def __init__(self, X, y):
        self.N, self.P = X.shape
        self.y = np.asarray(y)
        assert self.y.shape[0] == self.N
        self.X = X

    def f(self, w):
        # print('yo')
        return np.sum(
            np.log1p(
                np.exp(
                    -self. y * (self.X @ w)
                )
            )
        )

    def mu(self, w):
        # print('w', w.shape)
        return sigmoid(-self.y * (self.X @ w))

    def grad(self, w):
        # print(self.X.T.shape)
        # print(self.y.shape)
        # print(self.mu(w).shape)
        return - self.X.T @ (self.y * self.mu(w))
    # def grad(self, w):
    #     return -np.sum(
    #         [sigmoid(self.alpha(i, w)) * self.y[i] * self.X[i]
    #          for i in range(self.N)], axis=0)

    def __repr__(self):
        return f"Logistic(X.shape={self.X.shape}, y.shape={self.y.shape}"
            
    
    def classify(ell, sol):
        prob = sigmoid(ell.X @ sol)
        return np.where(prob > 0.5, 1, -1)
            
                                                  

            
        
