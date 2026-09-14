"""
Combinatorial constructs.
"""

import itertools
import math
from ._combinatorics import _bell_number, _subfactorial
from ._construct_shared import _arr_vals, _arr_vals_of

# --- Combinatorics (trivial subset - no explosion risk) ---


def Fibonacci(f, c, solver_parameters, s):
    n = int(f(s[1], c))
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def Multinomial(f, c, solver_parameters, s):
    ks = [int(k) for k in _arr_vals(f, c, solver_parameters, s)]
    return math.factorial(sum(ks)) // math.prod(math.factorial(k) for k in ks)


def Subfactorial(f, c, solver_parameters, s):
    return _subfactorial(f(s[1], c))


def BellNumber(f, c, solver_parameters, s):
    return _bell_number(f(s[1], c))


# --- Combinatorics: enumeration (no output-size limit - see
# create_mathjson_solver's `blacklist` parameter to disable
# these for untrusted expression sources) ---


def PowerSet(f, c, solver_parameters, s):
    """
    ["PowerSet", array]
    All subsets of `array` (including the empty set and the
    full set itself), as an array of arrays. No output-size
    limit: a set of n elements has 2^n subsets.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    result = ["Array"]
    for r in range(len(vals) + 1):
        for combo in itertools.combinations(vals, r):
            result.append(["Array"] + list(combo))
    return result


def Permutations(f, c, solver_parameters, s):
    """
    ["Permutations", array] or ["Permutations", array, k]
    All ordered arrangements of `k` elements from `array`
    (default k = len(array)), as an array of arrays. No
    output-size limit.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    k = int(f(s[2], c)) if len(s) > 2 else len(vals)
    return ["Array"] + [["Array"] + list(p) for p in itertools.permutations(vals, k)]


def Combinations(f, c, solver_parameters, s):
    """
    ["Combinations", array, k]
    All unordered k-element subsets of `array`, as an array
    of arrays. No output-size limit.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    k = int(f(s[2], c))
    return ["Array"] + [
        ["Array"] + list(combo) for combo in itertools.combinations(vals, k)
    ]


def CartesianProduct(f, c, solver_parameters, s):
    """
    ["CartesianProduct", array1, array2, ...]
    All ordered tuples with one element drawn from each
    array, as an array of arrays. No output-size limit: the
    result has len(array1) * len(array2) * ... elements.
    """
    lists = [_arr_vals_of(f, c, solver_parameters, arg) for arg in s[1:]]
    return ["Array"] + [["Array"] + list(combo) for combo in itertools.product(*lists)]
