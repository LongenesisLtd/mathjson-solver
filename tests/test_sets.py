import sys
import os
import pytest


sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["In", 2, ["Array", 1, 2, 3]], True),
        ({}, ["In", 4, ["Array", 1, 2, 3]], False),
        ({}, ["In", "Abc", ["Array", 1, 2, "Abc", 4]], True),
        ({}, ["In", "Abc", ["Array", 1, 2, "Abcd", 4]], False),
        ({}, ["In", ["Add", 2, 2], ["Array", 1, 4, 3]], True),
        ({}, ["In", ["Add", 2, 1], ["Array", 1, 2, ["Add", 1, 2]]], True),
        (
            {"a": 10, "b": 20},
            ["In", ["Add", "a", "b"], ["Array", 1, 2, ["Add", 15, 15], 4]],
            True,
        ),
        (
            {"a": 10, "b": 20},
            ["In", ["Add", "a", "b"], ["Array", 1, 2, ["Add", 15, 16], 4]],
            False,
        ),
        ({"a": [10, 20, 30]}, ["In", 20, "a"], True),
        ({"a": [10, 20, 30]}, ["In", 21, "a"], False),
        ({}, ["Not_in", 2, ["Array", 1, 2, 3]], False),
        ({}, ["Not_in", 4, ["Array", 1, 2, 3]], True),
        ({}, ["NotIn", 4, ["Array", 1, 2, 3]], True),
        ({"a": [10, 20, 30]}, ["Not_in", 20, "a"], False),
        ({"a": [10, 20, 30]}, ["Not_in", 21, "a"], True),
        ({}, ["Contains_any_of", ["Array", 1, 2, 3], ["Array", 1, 2, 3]], True),
        ({}, ["Contains_any_of", ["Array", 2, 3], ["Array", 1, 2]], True),
        ({}, ["Contains_any_of", ["Array", 1, 2, 3], ["Array", 3, 4, 5, 6]], True),
        ({}, ["Contains_any_of", ["Array", 1, 2, 3], ["Array", 4, 5, 6]], False),
        (
            {},
            [
                "Contains_any_of",
                ["Array", 1, ["Add", 1, 1], 6],
                ["Array", 4, 5, ["Add", 3, 3]],
            ],
            True,
        ),
        (
            {},
            [
                "Contains_any_of",
                ["Array", 1, ["Add", 1, 1], 3],
                ["Array", 4, 5, ["Add", 3, 3]],
            ],
            False,
        ),
        ({"a": [10, 20, 30]}, ["Contains_any_of", "a", ["Array", 1, 20, 3]], True),
        ({"b": [1, 20, 3]}, ["Contains_any_of", ["Array", 1, 2, 3], "b"], True),
        ({"b": [1, 20, 3]}, ["ContainsAnyOf", ["Array", 1, 2, 3], "b"], True),
        ({"a": [10, 20, 30], "b": [1, 20, 3]}, ["Contains_any_of", "a", "b"], True),
        ({"a": [10, 20, 30], "b": [1, 2, 3]}, ["Contains_any_of", "a", "b"], False),
        ({}, ["Contains_all_of", ["Array", 1, 2, 3], ["Array", 1, 2, 3]], True),
        ({}, ["Contains_all_of", ["Array", 1, 2], ["Array", 1, 2, 3]], False),
        ({}, ["Contains_all_of", ["Array", 1, 2, 3], ["Array", 1, 2]], True),
        ({}, ["Contains_all_of", ["Array", 1, 2, 3], ["Array", 2]], True),
        ({}, ["ContainsAllOf", ["Array", 1, 2, 3], ["Array", 2]], True),
        ({"a": [10, 20, 30], "b": [1, 20, 3]}, ["Contains_all_of", "a", "b"], False),
        ({"a": [1, 2, 3], "b": [1, 2]}, ["Contains_all_of", "a", "b"], True),
        ({}, ["Contains_none_of", ["Array", 1, 2, 3], ["Array", 1, 2, 3]], False),
        ({}, ["Contains_none_of", ["Array", 1, 2], ["Array", 2, 3]], False),
        ({}, ["ContainsNoneOf", ["Array", 1, 2], ["Array", 2, 3]], False),
        ({}, ["Contains_none_of", ["Array", 1, 2, 3], ["Array", 4, 5]], True),
    ],
)
def test_solver_simple(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
