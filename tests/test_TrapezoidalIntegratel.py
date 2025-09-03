import sys
import os
import pytest


NUMPY_AVAILABLE = False
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None


sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def _create_numpy_test_cases():
    """Create test cases that require numpy, only if numpy is available."""
    if not NUMPY_AVAILABLE:
        return []

    return [
        # 1. Polynomial Function f(x) = x²
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Power", "x", 2],
                0,
                1,
                10,
                ["Variable", "x"],
            ],
            np.float64(0.3350000000000001),
        ),
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Power", ["Variable", "x"], 2],
                0,
                1,
                10,
                ["Variable", "x"],
            ],
            np.float64(0.3350000000000001),
        ),
        # 2. Trigonometric Function f(x) = sin(x)
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Sin", ["Variable", "x"]],
                0,
                ["Pi"],
                100,
                ["Variable", "x"],
            ],
            np.float64(1.9998355038874436),
        ),
        # 3. Exponential Function f(x) = e^x
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Exp", ["Variable", "x"]],
                0,
                1,
                100,
                ["Variable", "x"],
            ],
            np.float64(1.7182961474504177),
        ),
        # 4. Rational Function f(x) = 1/(1+x²)
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Divide", 1, ["Add", 1, ["Power", ["Variable", "x"], 2]]],
                0,
                1,
                100,
                ["Variable", "x"],
            ],
            np.float64(0.7853939967307823),
        ),
        # 5. Product of Functions f(x) = x·sin(x)
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Multiply", ["Variable", "x"], ["Sin", ["Variable", "x"]]],
                0,
                ["Pi"],
                100,
                ["Variable", "x"],
            ],
            np.float64(3.1413342637004176),
        ),
        # 6. Logarithmic Function f(x) = ln(x)
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Ln", ["Variable", "x"]],
                1,
                2,
                100,
                ["Variable", "x"],
            ],
            np.float64(0.38629019447752866),
        ),
        # 7. Function with Singularity f(x) = 1/√x
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Divide", 1, ["Sqrt", ["Variable", "x"]]],
                0.01,
                1,
                100,
                ["Variable", "x"],
            ],
            np.float64(1.8038847804497282),
        ),
        # 8. Highly Oscillatory Function f(x) = sin(10x)·cos(3x)
        (
            {},
            [
                "TrapezoidalIntegrate",
                [
                    "Multiply",
                    ["Sin", ["Multiply", 10, ["Variable", "x"]]],
                    ["Cos", ["Multiply", 3, ["Variable", "x"]]],
                ],
                0,
                ["Multiply", 2, ["Pi"]],
                100,
                ["Variable", "x"],
            ],
            np.float64(5.787724498767512e-16),  # effectively zero
        ),
        # 9. Function with Multiple Local Extrema x²·sin(1/x)
        (
            {},
            [
                "TrapezoidalIntegrate",
                [
                    "Multiply",
                    ["Power", ["Variable", "x"], 2],
                    ["Sin", ["Divide", 1, ["Variable", "x"]]],
                ],
                0.1,
                1,
                500,
                ["Variable", "x"],
            ],
            np.float64(0.2866184933855661),
        ),
        # 10. Rapidly Varying Function f(x) = e^(-x²)
        (
            {},
            [
                "TrapezoidalIntegrate",
                [
                    "Exp",
                    ["Multiply", -1, ["Power", ["Variable", "x"], 2]],
                ],
                -5,
                5,
                500,
                ["Variable", "x"],
            ],
            np.float64(1.7724538509027818),
        ),
        # 11. Function with Discontinuity f(x) = 1/x
        (
            {},
            [
                "TrapezoidalIntegrate",
                ["Divide", 1, ["Variable", "x"]],
                0.001,
                1,
                1000,
                ["Variable", "x"],
            ],
            np.float64(6.984825983783107),  # 6.90776 is more accurate
        ),
        # 12. Function with Sharp Peak f(x) = 1/(1+100x²)
        (
            {},
            [
                "TrapezoidalIntegrate",
                [
                    "Divide",
                    1,
                    ["Add", 1, ["Multiply", 100, ["Power", ["Variable", "x"], 2]]],
                ],
                -1,
                1,
                1000,
                ["Variable", "x"],
            ],
            np.float64(0.29422552179014305),
        ),
    ]


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
@pytest.mark.parametrize(
    "parameters, expression, expected_result", _create_numpy_test_cases()
)
def test_integrals(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
