import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, [], None),
        ({}, ["Add", 2, 4, 3], 9),
        ({}, ["Sum", 2, 4, 3], 9),
        ({}, ["Sum", 2, 4, 3, None], 9),
        ({}, ["Add", 2, 4, "3"], 9),
        ({}, ["Sum", 2, 4, "3"], 9),
        ({}, ["Sum", 2, 4, "3", "abc"], 9),
        ({}, ["Sum", ["Array", 1, 1], 4, 3], 9),
        ({}, ["Sum", ["Array", 2, 4, 3]], 9),
        ({"a": 2}, ["Sum", "a", 4, 3], 9),
        ({"a": ["Array", 1, 1]}, ["Sum", "a"], 2),
        ({"a": ["Array", 1, 1]}, ["Sum", "a", 4, 3], 9),
        ({}, ["Subtract", 10, 5, 2], 3),
        ({}, ["Add", 5, 4, ["Negate", 3]], 6),
        ({}, ["Multiply", 2, 3, 4], 24),
        ({}, ["Divide", 10, 5], 2),
        ({}, ["Divide", 10, 4], 2.5),
        ({}, ["Power", 2, 3], 8),
        ({}, ["Root", 9, 2], 3),
        ({}, ["Root", 8, 3], 2),
        ({}, ["Sqrt", 9], 3),
        ({}, ["Square", 4], 16),
        ({}, ["Round", ["Exp", 2], 3], 7.389),
        ({}, ["Divide", 10, ["Add", 2, 3]], 2),
        ({}, ["Round", ["Log", 2.7183], 3], 1.0),
        ({}, ["Log2", 8], 3),
        ({}, ["Log10", 1000], 3),
    ],
)
def test_solver_arithmetics(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
