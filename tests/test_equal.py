import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["Equal", 10, 10], True),
        ({}, ["Equal", 10, 12], False),
        ({}, ["Equal", "aaa", "aaa"], True),
        ({}, ["Equal", "aaa", "baa"], False),
        ({}, ["Equal", "aaa", 11], False),
        ({}, ["Equal", None, "1"], False),
        ({}, ["Equal", 1, "1"], True),
        ({}, ["Equal", None, False], True),
        ({}, ["StrictEqual", 1, "1"], False),
        ({}, ["StrictEqual", 10, 10], True),
        ({}, ["StrictEqual", 10, 12], False),
        ({}, ["StrictEqual", "aaa", "aaa"], True),
        ({}, ["StrictEqual", "aaa", "baa"], False),
        ({}, ["StrictEqual", "aaa", 11], False),
        ({}, ["StrictEqual", None, "1"], False),
        ({}, ["Equal", None, False], True),
        ({}, ["Greater", 1, 2], False),
        ({}, ["Greater", 2, -2], True),
        ({}, ["Greater", "2", -2], True),
        ({}, ["GreaterEqual", 1, 1], True),
        ({}, ["GreaterEqual", 2, 1], True),
        ({}, ["GreaterEqual", 2, "1"], True),
        ({}, ["GreaterEqual", 0, 0], True),
        ({}, ["GreaterEqual", 1, 2], False),
        ({}, ["Less", 1, 1], False),
        ({}, ["Less", 1, 2], True),
        ({}, ["LessEqual", 1, 1], True),
        ({}, ["LessEqual", 1, 2], True),
        # NotEqual
        ({}, ["NotEqual", 1, 1], False),
        ({}, ["NotEqual", 1, 2], True),
        ({}, ["NotEqual", "aaa", "bbb"], True),
        ({}, ["NotEqual", "aaa", 0], True),
    ],
)
def test_solver_comparison(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
