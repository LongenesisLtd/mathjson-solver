import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver, extract_variables


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- Head / Tail: operate on the raw, unevaluated expression ---
        ({}, ["Head", ["Add", 1, 2]], "Add"),
        ({}, ["Head", ["Multiply", "x", 2]], "Multiply"),
        ({}, ["Head", 5], None),  # not a compound expression
        ({}, ["Tail", ["Add", 1, 2]], ["Array", 1, 2]),
        ({}, ["Tail", ["Multiply", "x", 2]], ["Array", "x", 2]),
        ({}, ["Tail", 5], ["Array"]),
        # --- Hold: returns its argument unevaluated ---
        ({}, ["Hold", ["Add", 1, 2]], ["Add", 1, 2]),
        ({"x": 5}, ["Hold", "x"], "x"),
        # --- Identity ---
        ({}, ["Identity", 42], 42),
        ({}, ["Identity", ["Add", 1, 2]], 3.0),  # Identity DOES evaluate its argument
        # --- Type ---
        ({}, ["Type", 5], "number"),
        ({}, ["Type", 5.5], "number"),
        ({}, ["Type", "hello"], "string"),
        ({}, ["Type", True], "boolean"),
        ({}, ["Type", ["Array", 1, 2]], "array"),
        ({}, ["Type", ["Rational", 1, 3]], "number"),
        # --- IsSame / Same: structural, not value, comparison ---
        ({}, ["IsSame", ["Add", 1, 2], ["Add", 1, 2]], True),
        ({}, ["IsSame", ["Add", 1, 2], ["Add", 2, 1]], False),
        ({}, ["IsSame", 3, 3], True),
        ({}, ["Same", ["Add", "x", 1], ["Add", "x", 1]], True),
        ({}, ["Same", ["Add", "x", 1], ["Add", "y", 1]], False),
    ],
)
def test_core(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


# --- extract_variables: Head/Tail/Hold/IsSame/Same never evaluate
# their arguments, so those arguments contribute no free variables. ---


def test_extract_variables_head_tail_hold_are_opaque():
    assert extract_variables(["Head", ["Add", "x", 1]], set(), set()) == set()
    assert extract_variables(["Tail", ["Add", "x", 1]], set(), set()) == set()
    assert extract_variables(["Hold", ["Multiply", "y", 2]], set(), set()) == set()


def test_extract_variables_is_same_is_opaque():
    result = extract_variables(
        ["IsSame", ["Add", "x", 1], ["Add", "x", 1]], set(), set()
    )
    assert result == set()


def test_extract_variables_finds_real_variable_alongside_hold():
    result = extract_variables(["Add", "z", ["Hold", "w"]], set(), set())
    assert result == {"z"}


def test_extract_variables_type_does_find_its_argument():
    # Unlike Head/Tail/Hold, Type genuinely evaluates its argument.
    result = extract_variables(["Type", "x"], set(), set())
    assert result == {"x"}
