"""
Number-theory constructs, backed by the algorithms in _number_theory.py.
"""

from fractions import Fraction
import math
from ._number_theory import (
    _MAX_NTH_PRIME,
    _MAX_NUMBER_THEORY_MAGNITUDE,
    _MAX_PRIME_PI,
    _bernoulli,
    _carmichael_lambda,
    _chinese_remainder,
    _continued_fraction,
    _digits_in_base,
    _divisors,
    _extended_gcd,
    _factor_integer,
    _from_continued_fraction,
    _is_figurate,
    _is_perfect_power,
    _is_prime,
    _jacobi_symbol,
    _lucas_l,
    _multiplicative_order,
    _primitive_root,
    _totient,
)
from ._construct_shared import _arr_vals, _arr_vals_of


def IsPrime(f, c, solver_parameters, s):
    return _is_prime(f(s[1], c))


# --- Number theory ---


def FactorInteger(f, c, solver_parameters, s):
    return ["Array"] + [["Array", p, e] for p, e in _factor_integer(f(s[1], c))]


def PrimeFactors(f, c, solver_parameters, s):
    return ["Array"] + [p for p, _ in _factor_integer(f(s[1], c))]


def PrimeNu(f, c, solver_parameters, s):
    return len(_factor_integer(f(s[1], c)))


def PrimeOmega(f, c, solver_parameters, s):
    return sum(e for _, e in _factor_integer(f(s[1], c)))


def Radical(f, c, solver_parameters, s):
    return math.prod(p for p, _ in _factor_integer(f(s[1], c)))


def IsSquareFree(f, c, solver_parameters, s):
    return all(e == 1 for _, e in _factor_integer(f(s[1], c)))


def Divisors(f, c, solver_parameters, s):
    return ["Array"] + _divisors(f(s[1], c))


def Sigma0(f, c, solver_parameters, s):
    return len(_divisors(f(s[1], c)))


def Sigma1(f, c, solver_parameters, s):
    return sum(_divisors(f(s[1], c)))


def SigmaMinus1(f, c, solver_parameters, s):
    return sum(Fraction(1, d) for d in _divisors(f(s[1], c)))


def DivisorSigma(f, c, solver_parameters, s):
    k = int(f(s[2], c))
    return sum(d**k for d in _divisors(f(s[1], c)))


def Totient(f, c, solver_parameters, s):
    return _totient(f(s[1], c))


def IsPerfectPower(f, c, solver_parameters, s):
    return _is_perfect_power(f(s[1], c))


def NthPrime(f, c, solver_parameters, s):
    """
    ["NthPrime", n]
    The n-th prime number (1-indexed: NthPrime(1) = 2).
    Capped at _MAX_NTH_PRIME - a naive forward search gets
    slow well before Python's own integer limits do.
    """
    n = int(f(s[1], c))
    if not (1 <= n <= _MAX_NTH_PRIME):
        raise ValueError(f"'NthPrime' n must be between 1 and {_MAX_NTH_PRIME}.")
    count, candidate = 0, 1
    while count < n:
        candidate += 1
        if _is_prime(candidate):
            count += 1
    return candidate


def NextPrime(f, c, solver_parameters, s):
    """
    ["NextPrime", n] or ["NextPrime", n, k]
    The smallest prime greater than n, or the k-th such
    prime. Both the starting value's magnitude and k are
    capped, for the same reason as NthPrime.
    """
    start = int(f(s[1], c))
    k = int(f(s[2], c)) if len(s) > 2 else 1
    if abs(start) > _MAX_NUMBER_THEORY_MAGNITUDE:
        raise ValueError(
            f"'NextPrime' starting value is limited to "
            f"{_MAX_NUMBER_THEORY_MAGNITUDE} in absolute value."
        )
    if not (1 <= k <= _MAX_NTH_PRIME):
        raise ValueError(f"'NextPrime' k must be between 1 and {_MAX_NTH_PRIME}.")
    count, candidate = 0, start
    while count < k:
        candidate += 1
        if _is_prime(candidate):
            count += 1
    return candidate


def PrimePi(f, c, solver_parameters, s):
    """
    ["PrimePi", n]
    pi(n): the count of primes <= n. Capped at
    _MAX_PRIME_PI - cost scales with n itself, not sqrt(n).
    """
    n = int(f(s[1], c))
    if not (0 <= n <= _MAX_PRIME_PI):
        raise ValueError(f"'PrimePi' n must be between 0 and {_MAX_PRIME_PI}.")
    return sum(1 for k in range(2, n + 1) if _is_prime(k))


def ExtendedGCD(f, c, solver_parameters, s):
    return ["Array"] + list(_extended_gcd(int(f(s[1], c)), int(f(s[2], c))))


def ChineseRemainder(f, c, solver_parameters, s):
    """
    ["ChineseRemainder", remainders, moduli]
    Solves the system x = remainders[i] (mod moduli[i]) via
    the Chinese Remainder Theorem. Moduli must be pairwise
    coprime.
    """
    remainders = _arr_vals_of(f, c, solver_parameters, s[1])
    moduli = _arr_vals_of(f, c, solver_parameters, s[2])
    return _chinese_remainder(remainders, moduli)


def CarmichaelLambda(f, c, solver_parameters, s):
    return _carmichael_lambda(f(s[1], c))


def JacobiSymbol(f, c, solver_parameters, s):
    return _jacobi_symbol(f(s[1], c), f(s[2], c))


def MultiplicativeOrder(f, c, solver_parameters, s):
    return _multiplicative_order(f(s[1], c), f(s[2], c))


def PrimitiveRoot(f, c, solver_parameters, s):
    return _primitive_root(f(s[1], c))


def LucasL(f, c, solver_parameters, s):
    return _lucas_l(f(s[1], c))


def BernoulliB(f, c, solver_parameters, s):
    return _bernoulli(f(s[1], c))


def ContinuedFraction(f, c, solver_parameters, s):
    x = f(s[1], c)
    max_terms = int(f(s[2], c)) if len(s) > 2 else 20
    return ["Array"] + _continued_fraction(x, max_terms)


def FromContinuedFraction(f, c, solver_parameters, s):
    return _from_continued_fraction(_arr_vals(f, c, solver_parameters, s))


def IntegerDigits(f, c, solver_parameters, s):
    base = int(f(s[2], c)) if len(s) > 2 else 10
    return ["Array"] + _digits_in_base(f(s[1], c), base)


def DigitCount(f, c, solver_parameters, s):
    base = int(f(s[2], c)) if len(s) > 2 else 10
    return len(_digits_in_base(f(s[1], c), base))


def DigitSum(f, c, solver_parameters, s):
    base = int(f(s[2], c)) if len(s) > 2 else 10
    return sum(_digits_in_base(f(s[1], c), base))


def FromDigits(f, c, solver_parameters, s):
    digits = _arr_vals(f, c, solver_parameters, s)
    base = int(f(s[2], c)) if len(s) > 2 else 10
    result = 0
    for d in digits:
        result = result * base + int(d)
    return result


def IsSquare(f, c, solver_parameters, s):
    n = int(f(s[1], c))
    return n >= 0 and math.isqrt(n) ** 2 == n


def IsTriangular(f, c, solver_parameters, s):
    return _is_figurate(f(s[1], c), lambda k: k * (k + 1) // 2, 0)


def IsPentagonal(f, c, solver_parameters, s):
    return _is_figurate(f(s[1], c), lambda k: k * (3 * k - 1) // 2, 1)


def IsOctahedral(f, c, solver_parameters, s):
    return _is_figurate(f(s[1], c), lambda k: k * (2 * k * k + 1) // 3, 1)


def IsCenteredSquare(f, c, solver_parameters, s):
    return _is_figurate(f(s[1], c), lambda k: 2 * k * (k - 1) + 1, 1)


def IsPerfect(f, c, solver_parameters, s):
    n = f(s[1], c)
    return sum(_divisors(n)[:-1]) == n


def IsAbundant(f, c, solver_parameters, s):
    n = f(s[1], c)
    return sum(_divisors(n)[:-1]) > n


def IsHappy(f, c, solver_parameters, s):
    n = int(f(s[1], c))
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1
