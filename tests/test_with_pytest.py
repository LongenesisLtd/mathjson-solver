import sys
import os
import pytest
import re

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver, MathJSONException


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
        ({}, ["Equal", "aaa", "aaa"], True),
        ({}, ["Equal", "aaa", "baa"], False),
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
        ({"color": "green"}, ["Switch", "undefined", 0, ["blue", 10], ["red", 30]], 0),
        ({}, ["If", [["Equal", 1, 0], 10], [["Equal", 2, 2], 20], 9000], 20),
        ({}, ["Array", 1, 2, 3, 5, 2], ["Array", 1, 2, 3, 5, 2]),
        ({}, ["Max", ["Array", 1, 2, 3, 5, 2]], 5),
        ({}, ["Max", ["Array", 1, 2, ["Sum", 2, 4, 3], 5, 2]], 9),
        ({}, ["Median", ["Array", 1, 2, 3, 5, 2]], 2),
        ({}, ["Average", ["Array", 1, 2, 3, 5, 2]], 2.6),
        (
            {},
            [
                "Average",
                [
                    "Array",
                    "-2",
                    -1,
                    "0",
                    1,
                    "2",
                    "3",
                    4,
                    5,
                    6,
                    "seven",
                    8,
                    "9",
                    "10",
                    15,
                    10,
                ],
            ],
            5.0,
        ),
        ({}, ["Average", ["Array"]], None),
        ({"a": 10, "b": 20}, ["Average", ["Array", "a", "b"]], 15),
        ({}, ["Length", ["Array", 1, 2, 3, 5, 2, 9]], 6),
        ({}, ["Length", ["Array"]], 0),
        ({}, ["Int", "12"], 12),
        ({}, ["Int", "12.2"], 12),
        ({}, ["Float", "12.2"], 12.2),
        ({}, ["Any", ["Array", 0, 0, False, 0, 0]], False),
        ({}, ["Any", ["Array", 0, 1, False, 0, 0]], True),
        ({}, ["All", ["Array", 0, 1, False, 0, 0]], False),
        ({}, ["All", ["Array", 0, 1, False, "", 0]], False),
        ({}, ["All", ["Array", 2, 1, True, "zz", 2]], True),
        ({}, ["Str", 12], "12"),
        ({}, ["Str", "12"], "12"),
        ({}, ["Str", "aabb"], "aabb"),
        ({}, "aabb", "aabb"),
        ({}, 11, 11),
        ({}, True, True),
        ({}, False, False),
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
    ],
)
def test_solver_simple(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_raises_divide():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape("Problem in Divide. ['Divide', 1, 0]. division by zero"),
    ):
        r = solver(["Divide", 1, 0])


def test_raises_unsupported():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape(
            "Problem in MathJSON. ['Unsupported', 1]. 'Unsupported' is not supported"
        ),
    ):
        r = solver(["Unsupported", 1])


def test_raises_malformed():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape("Problem in Power. ['Power', 1]. list index out of range"),
    ):
        r = solver(["Power", 1])


def test_handle_exception():
    solver = create_solver({})
    try:
        r = solver(["Power", 1])
    except MathJSONException:
        assert True
    else:
        assert False
