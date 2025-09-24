"""
Simple test cases for Reduce functionality

These tests verify that Reduce works with three variables:
- accumulator: carries state between iterations
- current_item: the current element from the array being reduced
- index: the current position in the array (0-based)
"""

import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def test_reduce_simple_sum():
    """
    Test 1: Simple sum using Reduce

    This should behave like: [1, 2, 3, 4].reduce((acc, item, index) => acc + item, 0)
    Expected: 0 + 1 + 2 + 3 + 4 = 10
    """
    parameters = {}

    expression = [
        "Reduce",
        ["Array", 1, 2, 3, 4],  # array to reduce
        0,  # initial accumulator value
        ["Add", "accumulator", "current_item"],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    expected_result = 10
    solver = create_solver(parameters)
    result = solver(expression)

    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_reduce_with_index_and_state():
    """
    Test 2: More complex reduction using accumulator, current_item, and index

    This calculates: sum of (item * index) + previous_sum
    For array [5, 10, 15]:
    - Index 0: acc=0, item=5, index=0 → result = 0 + (5 * 0) = 0
    - Index 1: acc=0, item=10, index=1 → result = 0 + (10 * 1) = 10
    - Index 2: acc=10, item=15, index=2 → result = 10 + (15 * 2) = 40
    Expected: 40
    """
    parameters = {}

    expression = [
        "Reduce",
        ["Array", 5, 10, 15],  # array to reduce
        0,  # initial accumulator value
        ["Add", ["Variable", "accumulator"], ["Multiply", "current_item", "index"]],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    expected_result = 40  # 0 + (5*0) + (10*1) + (15*2) = 0 + 0 + 10 + 30 = 40
    solver = create_solver(parameters)
    result = solver(expression)

    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_reduce_complex_accumulator():
    """
    Test 3: Reduce with complex accumulator state (for future NCI-like calculations)

    This simulates tracking multiple values in the accumulator.
    We'll use a simple pattern: accumulator starts as 0, but we build up
    both a sum and a product-like calculation.

    For simplicity, let's just track running sum where each iteration adds:
    (previous_sum + current_item + index)

    For array [2, 3, 1]:
    - Index 0: acc=0, item=2, index=0 → result = 0 + 2 + 0 = 2
    - Index 1: acc=2, item=3, index=1 → result = 2 + 3 + 1 = 6
    - Index 2: acc=6, item=1, index=2 → result = 6 + 1 + 2 = 9
    Expected: 9
    """
    parameters = {}

    expression = [
        "Reduce",
        ["Array", 2, 3, 1],  # array to reduce
        0,  # initial accumulator
        ["Add", "accumulator", "current_item", "index"],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    expected_result = 9  # ((0 + 2 + 0) + 3 + 1) + 1 + 2 = 2 + 4 + 3 = 9
    solver = create_solver(parameters)
    result = solver(expression)

    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_reduce_simple_sum_with_calculated_initial():
    """
    Test 4: Simple sum using Reduce

    Expected: (2+3) + 1 + 2 + 3 + 4 = 15
    """
    parameters = {}

    expression = [
        "Reduce",
        ["Array", 1, 2, 3, 4],  # array to reduce
        ["Add", 2, 3],  # initial accumulator value
        ["Add", "accumulator", "current_item"],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    expected_result = 15
    solver = create_solver(parameters)
    result = solver(expression)

    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_reduce_simple_sum_with_calculated_initial_and_calculated_list():
    """
    Test 5: Simple sum using Reduce

    Expected: (2+3) + (2+3) = 10
    """
    parameters = {}

    expression = [
        "Reduce",
        ["Slice", ["Array", 0, 1, 2, 3, 4], 2, 4],  # array to reduce
        ["Add", 2, 3],  # initial accumulator value
        ["Add", "accumulator", "current_item"],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    expected_result = 10
    solver = create_solver(parameters)
    result = solver(expression)

    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_reduce_with_array_acumulator():
    """
    Test 6: Simple sum using Reduce


    Expected: appending elements one by one resulting in the same array as beginning with ["Array", 1, 2, 3, 4]
    """
    parameters = {}

    expression = [
        "Reduce",
        ["Array", 1, 2, 3, 4],  # array to reduce
        ["Array"],  # initial accumulator value
        ["Appended", "accumulator", "current_item"],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    expected_result = ["Array", 1, 2, 3, 4]
    solver = create_solver(parameters)
    result = solver(expression)

    assert result == expected_result, f"Expected {expected_result}, got {result}"


if __name__ == "__main__":
    """Manual testing of the reduce cases"""
    print("Testing Reduce functionality...")

    try:
        test_reduce_simple_sum()
        print("✅ Test 1: Simple sum passed")
    except Exception as e:
        print(f"❌ Test 1: Simple sum failed - {e}")

    try:
        test_reduce_with_index_and_state()
        print("✅ Test 2: Index and state passed")
    except Exception as e:
        print(f"❌ Test 2: Index and state failed - {e}")

    try:
        test_reduce_complex_accumulator()
        print("✅ Test 3: Complex accumulator passed")
    except Exception as e:
        print(f"❌ Test 3: Complex accumulator failed - {e}")

    print("\nAll tests completed!")
