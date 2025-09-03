import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def test_CumulativeProduct1():
    parameters = {"test_array": ["Array", 2, 3, 4, 5]}

    expression = ["CumulativeProduct", "test_array"]

    expected_result = ["Array", 2, 6, 24, 120]
    solver = create_solver(parameters)
    # assert solver(expression) == expected_result
    assert solver(expression) == expected_result
