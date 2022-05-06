import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["Add", 2, 4, 3], 9),
        ({}, ["Sum", 2, 4, 3], 9),
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
        ({}, ["Equal", 10, 10], True),
        ({}, ["Equal", 10, 12], False),
        ({}, ["Abs", -3.5], 3.5),
        ({}, ["Round", -5.123456, 2], -5.12),
        ({}, ["Round", -5.123456, 0], -5),
        ({}, ["Round", 5.4], 5),
        ({}, ["Round", 5.5], 6),
        ({}, ["Constants", ["a", 1], ["b", 2], "a"], 1),
        ({}, ["Constants", ["a", 1], ["b", 2], ["c", 100], ["Sum", "a", "b"]], 3),
        ({}, ["Constants", ["a", 1], ["b", ["Add", 2, "a"]], "b"], 3),
        ({"x": 1}, ["Add", 2, "x"], 3),
        ({"color": "red"}, ["Switch", "color", 0, ["blue", 10], ["red", 30]], 30),
        ({"color": "green"}, ["Switch", "color", 0, ["blue", 10], ["red", 30]], 0),
        ({}, ["If", [["Equal", 1,0], 10], [["Equal", 2,2], 20], 9000], 20),
    ],
)
def test_solver_simple(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
