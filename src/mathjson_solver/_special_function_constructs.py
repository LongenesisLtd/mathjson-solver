"""
Special-function constructs, backed by the iterative algorithms in
_special_functions.py, plus (where available) scipy.special.
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

SCIPY_AVAILABLE = False
try:
    from scipy import special as _scipy_special

    SCIPY_AVAILABLE = True
except ImportError:
    pass


def _require_scipy(construct_name):
    if not SCIPY_AVAILABLE:
        raise ImportError(
            f"'{construct_name}' requires 'scipy'. Install with "
            f"'pip install scipy' (or 'pip install "
            f"mathjson-solver[special-functions]')."
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


# --- scipy-gated: Bessel, Airy, Zeta, regularized gamma/beta ---
#
# Thin wrappers around scipy.special - unlike ErfInv/LambertW/AGM/
# EllipticK/EllipticE/Hypergeometric1F1/Hypergeometric2F1 above, there's
# no algorithm of this project's own to verify here, just an argument-
# convention mapping (verified against CortexJS's own documented
# examples below, each matching to full precision).


def BesselJ(f, c, solver_parameters, s):
    """["BesselJ", n, x] - Bessel function of the first kind."""
    _require_scipy("BesselJ")
    return _scipy_special.jv(f(s[1], c), f(s[2], c))


def BesselY(f, c, solver_parameters, s):
    """["BesselY", n, x] - Bessel function of the second kind."""
    _require_scipy("BesselY")
    return _scipy_special.yv(f(s[1], c), f(s[2], c))


def BesselI(f, c, solver_parameters, s):
    """["BesselI", n, x] - modified Bessel function of the first kind."""
    _require_scipy("BesselI")
    return _scipy_special.iv(f(s[1], c), f(s[2], c))


def BesselK(f, c, solver_parameters, s):
    """["BesselK", n, x] - modified Bessel function of the second kind."""
    _require_scipy("BesselK")
    return _scipy_special.kv(f(s[1], c), f(s[2], c))


def AiryAi(f, c, solver_parameters, s):
    """["AiryAi", x] - Airy function Ai(x)."""
    _require_scipy("AiryAi")
    return _scipy_special.airy(f(s[1], c))[0]


def AiryBi(f, c, solver_parameters, s):
    """["AiryBi", x] - Airy function Bi(x)."""
    _require_scipy("AiryBi")
    return _scipy_special.airy(f(s[1], c))[2]


def AiryAiPrime(f, c, solver_parameters, s):
    """["AiryAiPrime", x] - derivative of the Airy function Ai(x)."""
    _require_scipy("AiryAiPrime")
    return _scipy_special.airy(f(s[1], c))[1]


def AiryBiPrime(f, c, solver_parameters, s):
    """["AiryBiPrime", x] - derivative of the Airy function Bi(x)."""
    _require_scipy("AiryBiPrime")
    return _scipy_special.airy(f(s[1], c))[3]


def Zeta(f, c, solver_parameters, s):
    """["Zeta", s] - the Riemann zeta function."""
    _require_scipy("Zeta")
    return _scipy_special.zeta(f(s[1], c), 1)


def GammaRegularized(f, c, solver_parameters, s):
    """
    ["GammaRegularized", a, z] - the *upper* regularized incomplete
    gamma function, Q(a, z) = Γ(a, z) / Γ(a) - CortexJS's own
    definition (not the lower one, P(a, z), that a function named
    "regularized incomplete gamma" more often defaults to elsewhere;
    verified against CortexJS's own documented example,
    `GammaRegularized(3, 5)` = 0.12465201948308115 - `scipy`'s
    `gammainc` computes the *lower* form, `gammaincc` the upper one
    needed here).
    """
    _require_scipy("GammaRegularized")
    return _scipy_special.gammaincc(f(s[1], c), f(s[2], c))


def BetaRegularized(f, c, solver_parameters, s):
    """
    ["BetaRegularized", x, a, b] - the regularized incomplete beta
    function, I_x(a, b). Note the argument order: CortexJS puts `x`
    first, while `scipy.special.betainc` takes `(a, b, x)`.
    """
    _require_scipy("BetaRegularized")
    return _scipy_special.betainc(f(s[2], c), f(s[3], c), f(s[1], c))
