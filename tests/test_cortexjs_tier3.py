import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver, extract_variables


# --- If: CortexJS flat form, alongside the existing Python pair form ---


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({"x": 5}, ["If", ["Greater", "x", 3], 42, 99], 42),
        ({"x": 1}, ["If", ["Greater", "x", 3], 42, 99], 99),
        ({"x": 5}, ["If", ["Greater", "x", 3], 42], 42),
        ({"x": 1}, ["If", ["Greater", "x", 3], 42], None),
        (
            {},
            ["If", [["Equal", 1, 0], 10], [["Equal", 2, 2], 20], 9000],
            20,
        ),
        # A Python-pair condition that is a bare parameter reference is
        # still correctly disambiguated from the CortexJS flat form.
        ({"my_flag": True}, ["If", ["my_flag", "yes"], "no"], "yes"),
        ({"my_flag": False}, ["If", ["my_flag", "yes"], "no"], "no"),
    ],
)
def test_if_forms(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_if_cortexjs_form_requires_valid_arity():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["If", ["Greater", 1, 0]])


# --- Function / Map / Filter / Reduce: CortexJS lambda form ---


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        (
            {},
            ["Map", ["Array", 1, 2, 3, 4], ["Function", ["Multiply", "_", 2]]],
            ["Array", 2.0, 4.0, 6.0, 8.0],
        ),
        (
            {},
            ["Map", ["Array", 1, 2, 3], ["Function", ["Add", "n", 1], "n"]],
            ["Array", 2.0, 3.0, 4.0],
        ),
        # Legacy call-template form keeps working unchanged.
        ({}, ["Map", ["Array", 1, 2, 3], ["Square"]], ["Array", 1, 4, 9]),
        (
            {},
            ["Filter", ["Array", 1, 2, 3, 4, 5], ["Function", ["Greater", "_", 2]]],
            ["Array", 3, 4, 5],
        ),
        ({}, ["Filter", ["Array", 1, 2, 3], ["LessEqual"], 2], ["Array", 1, 2]),
        (
            {},
            ["Reduce", ["Array", 1, 2, 3, 4], ["Function", ["Add", "_1", "_2"]]],
            10.0,
        ),
        (
            {},
            [
                "Reduce",
                ["Array", 1, 2, 3, 4],
                ["Function", ["Add", "acc", "n"], "acc", "n"],
                0,
            ],
            10.0,
        ),
        ({}, ["Reduce", ["Array", 1, 2, 3, 4], ["Add"]], 10.0),
        (
            {},
            [
                "Reduce",
                ["Array", 1, 2, 3, 4],
                0,
                ["Add", "accumulator", "current_item"],
                ["Variable", "accumulator"],
                ["Variable", "current_item"],
                ["Variable", "index"],
            ],
            10.0,
        ),
        ({}, ["Product", ["Array", 5, 7, 11]], 385),
    ],
)
def test_function_map_filter_reduce(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_bare_function_expression_returns_unevaluated():
    solver = create_solver({})
    assert solver(["Function", ["Multiply", "_", 2]]) == [
        "Function",
        ["Multiply", "_", 2],
    ]


# --- Local scope correctly shadows top-level solver parameters ---


def test_constants_shadow_solver_parameter():
    solver = create_solver({"x": 5})
    assert solver(["Constants", ["x", 100], ["Add", "x", 1]]) == 101.0


def test_reduce_variable_shadows_solver_parameter():
    solver = create_solver({"x": 5})
    result = solver(
        [
            "Reduce",
            ["Array", 1, 2, 3, 4],
            0,
            ["Add", "accumulator", "x"],
            ["Variable", "accumulator"],
            ["Variable", "x"],
            ["Variable", "index"],
        ]
    )
    assert result == 10.0


def test_function_parameter_shadows_solver_parameter():
    solver = create_solver({"x": 5})
    result = solver(["Map", ["Array", 1, 2, 3], ["Function", ["Add", "x", 1], "x"]])
    assert result == ["Array", 2.0, 3.0, 4.0]


# --- extract_variables ---


def test_extract_variables_if_cortexjs_form():
    result = extract_variables(["If", ["Greater", "x", 3], "y", "z"], set(), set())
    assert result == {"x", "y", "z"}


def test_extract_variables_if_python_pair_bare_flag():
    result = extract_variables(["If", ["my_flag", "y"], "z"], set(), set())
    assert result == {"my_flag", "y", "z"}


def test_extract_variables_function_params_are_not_free_variables():
    result = extract_variables(
        ["Map", "arr", ["Function", ["Add", "acc", "extra"], "acc"]], set(), set()
    )
    assert result == {"arr", "extra"}
