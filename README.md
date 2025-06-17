# MathJSON Solver

[![PyPI](https://img.shields.io/pypi/v/mathjson-solver.svg)](https://pypi.org/project/mathjson-solver/)
[![PyPI Downloads](https://static.pepy.tech/badge/mathjson-solver/month)](https://pepy.tech/projects/mathjson-solver)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A reliable Python library for numerically evaluating mathematical expressions in MathJSON format. Perfect for applications that need to safely execute user-provided formulas, calculate dynamic equations, or process mathematical data.

**What is MathJSON?** MathJSON represents mathematical expressions as JSON arrays, like `["Add", 1, 2, 3]` for 1+2+3. This format is safe, structured, and easy to generate programmatically.

Inspired by [CortexJS Compute Engine](https://cortexjs.io/compute-engine/) though designed as an independent implementation focused on our specific use cases.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Operations](#supported-operations)
- [Error Handling](#error-handling)
- [Use Cases](#use-cases)
- [Testing](#testing)
- [Community](#community)
- [Contributing](#contributing)

## Installation

```bash
pip install mathjson-solver
```

**Requirements:** Python 3.7+

**Optional:** numpy (only required for `TrapezoidalIntegrate` function)

## Quick Start

```python
from mathjson_solver import create_solver, MathJSONException

# Define variables and create solver
parameters = {"x": 2, "y": 3}
solver = create_solver(parameters)

# Evaluate expressions
basic_math = solver(["Add", "x", "y", 4])
print(basic_math)  # 9 (because 2+3+4=9)

# More complex expressions
result = solver(["Multiply", ["Add", "x", 1], ["Subtract", "y", 1]])
print(result)  # 6 (because (2+1) * (3-1) = 6)

# Handle errors gracefully
try:
    solver(["Divide", 1, 0])
except MathJSONException as e:
    print(f"Math error: {e}")
    # Math error: Problem in Divide. ['Divide', 1, 0]. division by zero
```

## Supported Operations

The library supports a comprehensive set of mathematical operations:

* **Arithmetic:** Add, Sum, Subtract, Multiply, Divide, Negate, Power, Square, Root, Sqrt, Abs, Round
* **Trigonometry:** Sin, Cos, Tan, Arcsin, Arccos, Arctan
* **Logarithms:** Log, Log2, Log10, Exp
* **Comparison:** Equal, StrictEqual, NotEqual, Greater, GreaterEqual, Less, LessEqual
* **Logic & Sets:** Any, All, Not, In, NotIn, ContainsAnyOf, ContainsAllOf, ContainsNoneOf
* **Statistics:** Average, Max, Min, Median, Length
* **Arrays:** Array creation and manipulation with Map function
* **Control Flow:** If statements, Switch-Case, Constants definition
* **Type Conversion:** Int, Float, Str, IsDefined
* **Date/Time:** Strptime, Strftime, Today, Now, TimeDelta functions
* **Advanced:** HasMatchingSublist, TrapezoidalIntegrate (requires numpy), Variable references
* **Constants:** Pi

[View complete documentation with examples →](https://github.com/LongenesisLtd/mathjson-solver/blob/main/docs/README.md)

## Error Handling

MathJSON Solver raises `MathJSONException` for invalid expressions or mathematical errors:

```python
from mathjson_solver import create_solver, MathJSONException

solver = create_solver({})

# Handle specific math errors
try:
    result = solver(["Sqrt", -1])  # Invalid: square root of negative
except MathJSONException as e:
    print(f"Cannot evaluate: {e}")

# Handle malformed expressions
try:
    result = solver(["UnknownFunction", 1, 2])
except MathJSONException as e:
    print(f"Unsupported operation: {e}")
```

## Use Cases

* **Dynamic Formulas:** Let users create custom calculations in web applications
* **Scientific Computing:** Evaluate mathematical models with variable parameters
* **Business Logic:** Process complex pricing rules or scoring algorithms
* **Data Processing:** Apply mathematical transformations to datasets
* **Health Applications:** Calculate medical scores, dosages, or risk assessments

## Testing

Install development dependencies and run tests:

```bash
# Install pytest if not already installed
pip install pytest

# Run tests from project directory
pytest

# Run with coverage
pytest --cov=mathjson_solver
```

## Community

- **Questions & Discussion:** [GitHub Issues](https://github.com/LongenesisLtd/mathjson-solver/issues)
- **Bug Reports & Feature Requests:** [GitHub Issues](https://github.com/LongenesisLtd/mathjson-solver/issues)
- **Documentation:** [Complete Function Reference](https://github.com/LongenesisLtd/mathjson-solver/blob/main/docs/README.md)

## Contributing

We welcome contributions! Please feel free to:
- Report bugs or request features via [GitHub Issues](https://github.com/LongenesisLtd/mathjson-solver/issues)
- Submit pull requests with improvements


## License

[View license information](https://github.com/LongenesisLtd/mathjson-solver/blob/main/LICENSE)

---

Made with ❤️ by [Longenesis](https://longenesis.com/team)
