import numpy as np

def nu_fun(gamma):
    """Calculates nu based on risk aversion gamma."""
    if gamma == 1: return np.inf
    return 1.0 / np.sqrt(1.0 - gamma)

def C(tau, nu):
    """Helper function C(tau) from Eq 14."""
    # Using normalized time (nu * tau)
    return np.cosh(nu * tau) + nu * np.sinh(nu * tau)

def C_(tau, nu):
    """Derivative C'(tau) from Eq 13."""
    return nu * np.sinh(nu * tau) + (nu ** 2) * np.cosh(nu * tau)

def D(tau, gamma):
    """
    Calculates the position sizing factor D(tau).
    Normalized time input expected.
    """
    if gamma == 0:
        return 1.0 # Log utility D(tau) case - 1
    
    nu = nu_fun(gamma)
    c = C(tau, nu)
    Cp = C_(tau, nu)
    return Cp / c

def alpha(W, X, tau, k, gamma, sigma):
    tau_norm = tau * k
    D_val = D(tau_norm, gamma)
    # Scaling factor: k / sigma^2 (Derived from normalization section)
    scaling = k / (sigma ** 2)
    return -1 * W * X * scaling * D_val

def utility(W, gamma):
    if gamma == 0:
        return np.log(W)
    return (1 / gamma) * (W ** gamma)