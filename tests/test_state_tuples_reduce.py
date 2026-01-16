"""
Test demonstrating state tuples with Reduce for stateful accumulation

This test validates that we can use Reduce with tuple states to maintain
multiple accumulator variables, which is essential for implementing
the NCI discrete approximation method.
"""

import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def test_simple_state_tuple_accumulation():
    """
    Test basic state tuple: accumulate sum and count simultaneously
    This mimics pattern: each iteration updates two values and returns new tuple

    Based on the working test_reduce_with_array_acumulator pattern,
    but instead of appending, we build a new 2-element state array each time.
    """

    expression = [
        "Reduce",
        ["Array", 1, 2, 3, 4],  # Input array
        ["Array", 0, 0],  # Initial state: [sum=0, count=0]
        # Build a new array with updated values
        [
            "Appended",
            [
                "Appended",
                ["Array"],  # Start with empty array
                ["Add", ["AtIndex", "accumulator", 0], "current_item"],  # Add new sum
            ],
            ["Add", ["AtIndex", "accumulator", 1], 1],  # Add new count
        ],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    solver = create_solver({})
    result = solver(expression)

    # Result should be [sum=10, count=4]
    assert result == ["Array", 10, 4], f"Expected ['Array', 10, 4], got {result}"


def test_running_sum_and_product():
    """
    Test more complex state tuple: running sum and running product
    Equivalent to:
    sum = 0
    product = 1
    for x in [2, 3, 4]:
        sum += x
        product *= x
    # Result: sum=9, product=24
    """

    expression = [
        "Reduce",
        ["Array", 2, 3, 4],  # Input array
        ["Array", 0, 1],  # Initial state: [sum=0, product=1]
        # Build new state using nested Appended pattern
        [
            "Appended",
            [
                "Appended",
                ["Array"],
                [
                    "Add",
                    ["AtIndex", "accumulator", 0],
                    "current_item",
                ],  # new_sum = old_sum + item
            ],
            [
                "Multiply",
                ["AtIndex", "accumulator", 1],
                "current_item",
            ],  # new_product = old_product * item
        ],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    solver = create_solver({})
    result = solver(expression)

    # Result should be [sum=9, product=24]
    assert result == ["Array", 9, 24], f"Expected ['Array', 9, 24], got {result}"


def test_simple_dual_accumulation():
    """
    Test dual accumulation: sum and max in same state tuple
    Simpler example demonstrating the state tuple pattern
    """

    expression = [
        "Reduce",
        ["Array", 3, 1, 4, 2],  # Input array
        ["Array", 0, 0],  # Initial state: [sum=0, max=0]
        # Build new state using nested Appended pattern
        [
            "Appended",
            [
                "Appended",
                ["Array"],
                [
                    "Add",
                    ["AtIndex", "accumulator", 0],
                    "current_item",
                ],  # new_sum = old_sum + item
            ],
            [
                "Max",
                ["Array", ["AtIndex", "accumulator", 1], "current_item"],
            ],  # new_max = max(old_max, item)
        ],
        ["Variable", "accumulator"],
        ["Variable", "current_item"],
        ["Variable", "index"],
    ]

    solver = create_solver({})
    result = solver(expression)

    # Result should be [sum=10, max=4]
    assert result == ["Array", 10, 4], f"Expected ['Array', 10, 4], got {result}"


def test_extract_final_value_from_state_tuple():
    """
    Test that we can extract just the final accumulated value from a state tuple
    (the pattern we'll use for the NCI implementation)
    """

    expression = [
        "Constants",
        # Use Reduce to accumulate state tuple [sum, product]
        [
            "state_result",
            [
                "Reduce",
                ["Array", 2, 3, 4],
                ["Array", 0, 1],  # [sum=0, product=1]
                # Build new state using nested Appended pattern
                [
                    "Appended",
                    [
                        "Appended",
                        ["Array"],
                        ["Add", ["AtIndex", "accumulator", 0], "current_item"],  # sum
                    ],
                    [
                        "Multiply",
                        ["AtIndex", "accumulator", 1],
                        "current_item",
                    ],  # product
                ],
                ["Variable", "accumulator"],
                ["Variable", "current_item"],
                ["Variable", "index"],
            ],
        ],
        # Extract just the sum (index 0) - this is what we'll do for NCI risk
        ["AtIndex", "state_result", 0],
    ]

    solver = create_solver({})
    result = solver(expression)

    # Should return just the sum: 2 + 3 + 4 = 9
    assert result == 9, f"Expected 9, got {result}"
