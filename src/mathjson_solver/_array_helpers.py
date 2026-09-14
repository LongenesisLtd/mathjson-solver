"""
Element-wise array/vector arithmetic helpers, backing the
MultiplyByScalar/AddArray/CumulativeSum/... family of constructs.
"""

import numbers
from functools import reduce


def _MultiplyByScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x * a for x in l]


def _MultiplyByArray(
    l1: list[numbers.Real], l2: list[numbers.Real]
) -> list[numbers.Real]:
    return [a * b for a, b in zip(l1, l2)]


def _AddScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x + a for x in l]


def _SubtractScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x - a for x in l]


def _AddArray(l1: list[numbers.Real], l2: list[numbers.Real]) -> list[numbers.Real]:
    return [a + b for a, b in zip(l1, l2)]


def _SubtractArray(
    l1: list[numbers.Real], l2: list[numbers.Real]
) -> list[numbers.Real]:
    return [a - b for a, b in zip(l1, l2)]


def _CumulativeProduct(l: list) -> list:
    res = []
    for i, x in enumerate(l):
        if i == 0:
            res.append(x)
        else:
            res.append(reduce(lambda a, b: a * b, l[: i + 1]))
    return res


def _CumulativeSum(l: list) -> list:
    res = []
    for i, x in enumerate(l):
        if i == 0:
            res.append(x)
        else:
            res.append(reduce(lambda a, b: a + b, l[: i + 1]))
    return res
