import sys
import os
from fractions import Fraction
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- stdlib-based one-liners ---
        ({}, ["PowerMod", 4, 13, 497], pow(4, 13, 497)),
        ({}, ["ModularInverse", 3, 11], 4),
        ({}, ["IntegerSqrt", 50], 7),
        # --- divisors / factorization ---
        (
            {},
            ["FactorInteger", 360],
            ["Array", ["Array", 2, 3], ["Array", 3, 2], ["Array", 5, 1]],
        ),
        ({}, ["PrimeFactors", 360], ["Array", 2, 3, 5]),
        ({}, ["PrimeNu", 360], 3),
        ({}, ["PrimeOmega", 360], 6),
        ({}, ["Radical", 360], 30),
        ({}, ["Radical", 1], 1),
        ({}, ["IsSquareFree", 360], False),
        ({}, ["IsSquareFree", 30], True),
        ({}, ["IsSquareFree", 1], True),
        ({}, ["Divisors", 28], ["Array", 1, 2, 4, 7, 14, 28]),
        ({}, ["Sigma0", 28], 6),
        ({}, ["Sigma1", 28], 56),
        ({}, ["SigmaMinus1", 6], 2),  # sum of reciprocals of 1,2,3,6 = 2
        ({}, ["DivisorSigma", 28, 2], 1 + 4 + 16 + 49 + 196 + 784),
        ({}, ["Divides", 4, 28], True),
        ({}, ["Divides", 5, 28], False),
        ({}, ["Totient", 1], 1),
        ({}, ["Totient", 9], 6),
        ({}, ["Totient", 36], 12),
        ({}, ["Totient", 97], 96),  # prime
        ({}, ["IsPerfectPower", 27], True),
        ({}, ["IsPerfectPower", 15], False),
        ({}, ["IsPerfectPower", 1000000], True),
        # --- capped prime lookups ---
        ({}, ["NthPrime", 1], 2),
        ({}, ["NthPrime", 10], 29),
        ({}, ["NextPrime", 10], 11),
        ({}, ["NextPrime", 10, 3], 17),
        ({}, ["PrimePi", 100], 25),
        ({}, ["PrimePi", 0], 0),
        # --- modular arithmetic ---
        ({}, ["ExtendedGCD", 35, 15], ["Array", 5, 1, -2]),
        (
            {},
            ["ChineseRemainder", ["Array", 2, 3, 2], ["Array", 3, 5, 7]],
            23,
        ),
        ({}, ["CarmichaelLambda", 1], 1),
        ({}, ["CarmichaelLambda", 561], 80),  # first Carmichael number
        ({}, ["JacobiSymbol", 2, 7], 1),
        ({}, ["LegendreSymbol", 3, 7], -1),
        ({}, ["MultiplicativeOrder", 3, 7], 6),
        ({}, ["MultiplicativeOrder", 2, 7], 3),
        ({}, ["PrimitiveRoot", 7], 3),
        # --- sequences ---
        ({}, ["LucasL", 0], 2),
        ({}, ["LucasL", 4], 7),
        ({}, ["CatalanNumber", 0], 1),
        ({}, ["CatalanNumber", 4], 14),
        ({}, ["ContinuedFraction", 22 / 7], ["Array", 3, 7]),
        ({}, ["FromContinuedFraction", ["Array", 3, 7, 15, 1]], Fraction(355, 113)),
        # --- digit manipulation ---
        ({}, ["IntegerDigits", 12345], ["Array", 1, 2, 3, 4, 5]),
        ({}, ["IntegerDigits", 255, 16], ["Array", 15, 15]),
        ({}, ["DigitCount", 12345], 5),
        ({}, ["DigitSum", 12345], 15),
        ({}, ["FromDigits", ["Array", 1, 2, 3, 4, 5]], 12345),
        ({}, ["FromDigits", ["Array", 15, 15], 16], 255),
        # --- figurate / special-property predicates ---
        ({}, ["IsSquare", 49], True),
        ({}, ["IsSquare", 50], False),
        ({}, ["IsTriangular", 0], True),
        ({}, ["IsTriangular", 15], True),
        ({}, ["IsTriangular", 16], False),
        ({}, ["IsPentagonal", 12], True),
        ({}, ["IsPentagonal", 13], False),
        ({}, ["IsOctahedral", 6], True),
        ({}, ["IsOctahedral", 19], True),
        ({}, ["IsCenteredSquare", 13], True),
        ({}, ["IsCenteredSquare", 9], False),  # scraped formula would wrongly say True
        ({}, ["IsPerfect", 28], True),
        ({}, ["IsPerfect", 12], False),
        ({}, ["IsAbundant", 12], True),
        ({}, ["IsAbundant", 28], False),  # perfect, not abundant
        ({}, ["IsHappy", 19], True),
        ({}, ["IsHappy", 4], False),
    ],
)
def test_number_theory(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_bernoulli_b_uses_minus_one_half_convention():
    solver = create_solver({})
    assert solver(["BernoulliB", 0]) == 1
    assert solver(["BernoulliB", 1]) == Fraction(-1, 2)
    assert solver(["BernoulliB", 2]) == Fraction(1, 6)
    assert solver(["BernoulliB", 4]) == Fraction(-1, 30)
    assert solver(["BernoulliB", 3]) == 0


# --- Error paths: caps and domain requirements ---


def test_nth_prime_rejects_out_of_range():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["NthPrime", 0])
    with pytest.raises(Exception):
        solver(["NthPrime", 10**7])


def test_next_prime_rejects_excessive_starting_magnitude():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["NextPrime", 10**20])


def test_next_prime_rejects_excessive_k():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["NextPrime", 10, 10**7])


def test_prime_pi_rejects_out_of_range():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["PrimePi", 10**7])


def test_factor_integer_rejects_non_positive():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["FactorInteger", 0])
    with pytest.raises(Exception):
        solver(["Divisors", -5])


def test_factor_integer_rejects_excessive_magnitude():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["FactorInteger", 10**20])


def test_multiplicative_order_requires_coprime_inputs():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["MultiplicativeOrder", 2, 8])


def test_jacobi_symbol_requires_odd_positive_modulus():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["JacobiSymbol", 3, 8])
