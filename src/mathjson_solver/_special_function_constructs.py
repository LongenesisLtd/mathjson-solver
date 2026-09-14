"""
Special-function constructs, backed by the iterative algorithms in
_special_functions.py.
"""

import math
from ._special_functions import (
    _agm,
    _elliptic_k_e,
    _erf_inv,
    _hyp1f1,
    _hyp2f1,
    _lambert_w,
)

# --- Special functions ---


def Beta(f, c, solver_parameters, s):
    a, b = f(s[1], c), f(s[2], c)
    return math.gamma(a) * math.gamma(b) / math.gamma(a + b)


def Factorial2(f, c, solver_parameters, s):
    n = int(f(s[1], c))
    result = 1
    while n > 1:
        result *= n
        n -= 2
    return result


def ErfInv(f, c, solver_parameters, s):
    return _erf_inv(f(s[1], c))


def LambertW(f, c, solver_parameters, s):
    return _lambert_w(f(s[1], c))


def AGM(f, c, solver_parameters, s):
    return _agm(f(s[1], c), f(s[2], c))


def EllipticK(f, c, solver_parameters, s):
    return _elliptic_k_e(f(s[1], c))[0]


def EllipticE(f, c, solver_parameters, s):
    return _elliptic_k_e(f(s[1], c))[1]


def Hypergeometric1F1(f, c, solver_parameters, s):
    """["Hypergeometric1F1", a, b, z] - confluent hypergeometric function 1F1(a;b;z)."""
    return _hyp1f1(f(s[1], c), f(s[2], c), f(s[3], c))


def Hypergeometric2F1(f, c, solver_parameters, s):
    """["Hypergeometric2F1", a, b, c, z] - Gauss hypergeometric function 2F1(a,b;c;z)."""
    return _hyp2f1(f(s[1], c), f(s[2], c), f(s[3], c), f(s[4], c))
