# MathJSON Solver

[![PyPI](https://img.shields.io/pypi/v/mathjson-solver.svg)](https://pypi.org/project/mathjson-solver/)
[![PyPI Downloads](https://static.pepy.tech/badge/mathjson-solver/month)](https://pepy.tech/projects/mathjson-solver)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A reliable Python library for numerically evaluating mathematical expressions in MathJSON format. Perfect for applications that need to safely execute user-provided formulas, calculate dynamic equations, or process mathematical data.

**What is MathJSON?** MathJSON represents mathematical expressions as JSON arrays, like `["Add", 1, 2, 3]` for 1+2+3. This format is safe, structured, and easy to generate programmatically.

Coming from 1.x? Version 2 changed `Log`'s meaning — see [Migrating from 1.x](#migrating-from-1x).

## Table of Contents
- [Use Cases](#use-cases)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Operations](#supported-operations)
- [Restricting Available Functions](#restricting-available-functions)
- [Error Handling](#error-handling)
- [Migrating from 1.x](#migrating-from-1x)
- [Testing](#testing)
- [Community](#community)
- [Contributing](#contributing)
- [Related Projects](#related-projects)

## Use Cases

**The core pattern:** if your Python backend accepts user-provided datapoints *and* user-provided math to apply to them, mathjson-solver is the engine for that — it evaluates the formula without needing to trust either the formula's author or the data's source. A survey platform is a natural fit: a survey and its "calculated answers" both come from the same untrusted party (the survey builder), the calculation runs against whatever the respondent enters, and the result has to be safe to compute no matter what either of them contains. The same shape covers pricing rules, scoring algorithms, and scientific or medical calculators wherever the formula itself isn't fixed at development time — our showcase example is a breast-cancer risk calculator implementing the [Gail model](https://github.com/LongenesisLtd/mathjson-solver/blob/main/tests/test_gail_model.py), numerical integration included, entirely in MathJSON.

* **Dynamic Formulas:** Let users create custom calculations in web applications
* **Scientific Computing:** Evaluate mathematical models with variable parameters
* **Business Logic:** Process complex pricing rules or scoring algorithms
* **Data Processing:** Apply mathematical transformations to datasets
* **Health Applications:** Calculate medical scores, dosages, or risk assessments

**What's still missing:** a ready-to-use, user-facing editor for authoring MathJSON itself — today, the expressions have to come from somewhere else (a form builder, a generated JSON structure, hand-written JSON). CortexJS ships [MathLive's mathfield](https://mathlive.io/mathfield/) for entering math, but it's built for typing LaTeX-style notation (e-learning quizzes, scientific computing, calculators) — not for assembling a formula that references named fields from a form. Worth evaluating on its own merits rather than assumed to transfer.

## Installation

```bash
pip install mathjson-solver
```

**Requirements:** Python 3.10+

**Optional:**
- `pip install mathjson-solver[integration]` (installs numpy; only required for `TrapezoidalIntegrate`)
- `pip install mathjson-solver[regex]` (installs [google-re2](https://pypi.org/project/google-re2/); only required for `RegExp`/`IsMatch`/`StringMatch`/`StringMatchAll`)
- `pip install mathjson-solver[special-functions]` (installs [scipy](https://scipy.org/); required for `BesselJ`/`BesselY`/`BesselI`/`BesselK`, `AiryAi`/`AiryBi`/`AiryAiPrime`/`AiryBiPrime`, `Zeta`, `GammaRegularized`, `BetaRegularized`, and `CDF`/`Quantile` on `BinomialDistribution`/`PoissonDistribution`)

Combine any of these by separating them with commas in one `pip install`, e.g. `pip install mathjson-solver[integration,regex,special-functions]` for all three at once.

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

**Think Functional:** MathJSON Solver embraces functional programming principles. Instead of writing loops and modifying variables, you compose expressions that transform data. Functions like `Map`, `Reduce`, and `Filter` let you process arrays elegantly, while immutable operations ensure predictable, side-effect-free calculations. Don't worry if you're new to functional programming — the examples will guide you naturally into this powerful paradigm.

```python
# Functional approach: transform data with expressions
solver(["Map", ["Array", 1, 2, 3, 4], ["Multiply"], 2])  # [2, 4, 6, 8]
solver(["Reduce", ["Array", 1, 2, 3, 4], 0, ["Add", "acc", "item"],
        ["Variable", "acc"], ["Variable", "item"], ["Variable", "i"]])  # 10

# CortexJS-style forms also work: a lambda via Function, and a 2-argument Reduce
solver(["Map", ["Array", 1, 2, 3, 4], ["Function", ["Multiply", "_", 2]]])  # [2, 4, 6, 8]
solver(["Reduce", ["Array", 1, 2, 3, 4], ["Add"]])                          # 10
```

## Supported Operations

338 MathJSON constructs across arithmetic, trigonometry, logarithms, comparisons, logic and sets, statistics and probability distributions, functional programming (Map/Reduce/Filter), arrays and collections, control flow, strings and RE2-backed pattern matching, date/time, number theory, special functions (Bessel/Airy/Gamma/elliptic-integral/hypergeometric families), combinatorics, and structural introspection.

```python
["Add", 1, 2, ["Multiply", 3, 4]]                # 15
["CDF", ["NormalDistribution", 0, 1], 1.96]      # 0.975 (z-score to percentile)
["Reduce", ["Array", 1, 2, 3, 4], ["Add"]]       # 10
["StringMatch", "patient-042", "[0-9]+"]         # "042" at position 9-11
["FactorInteger", 360]                           # [[2,3], [3,2], [5,1]]  (2³·3²·5)
```

Three optional extras unlock specific functions — see [Installation](#installation) above: `regex` (RE2-backed pattern matching), `integration` (`TrapezoidalIntegrate`), `special-functions` (Bessel/Airy/Zeta/regularized gamma and beta, plus `CDF`/`Quantile` on the two discrete probability distributions).

[View the complete function reference with examples →](https://github.com/LongenesisLtd/mathjson-solver/blob/main/docs/README.md)

## Restricting Available Functions

Pass `blacklist` to disable specific constructs for a solver instance — useful when evaluating expressions from a source you don't fully trust, or when your deployment simply doesn't want certain functions exposed:

```python
solver = create_solver(parameters, blacklist=["PowerSet", "Permutations", "Combinations", "CartesianProduct"])
solver(["PowerSet", ["Array", 1, 2, 3]])
# Raises: MathJSONException: Problem in PowerSet. [...]. 'PowerSet' has been disabled in this solver instance.

solver(["Add", 1, 2])  # unaffected constructs still work: 3.0
```

**This is an access-policy control, not a resource limiter.** Blacklisting a construct stops it from running at all; it doesn't make an *enabled* construct safe against pathological input. In particular, the enumeration functions (`PowerSet`, `Permutations`, `Combinations`, `CartesianProduct`) have no built-in output-size limit — `["PowerSet", ["Range", 30]]` will try to materialize over a billion subsets if you let it run. If you're evaluating expressions from an untrusted source, blacklist any construct whose worst-case cost you haven't reasoned about, rather than assuming everything implemented is safe by default for every threat model.

A blacklisted name that isn't an actual construct (a typo, for instance) is silently ignored rather than rejected — `blacklist` isn't validated against the list of implemented constructs.

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

## Migrating from 1.x

> **Version 2 introduced a breaking change:** `Log` is now log base 10 instead of natural log (see [CHANGELOG.md](CHANGELOG.md)). Bugfix releases for the 1.x line continue on the [`1.x` branch](https://github.com/LongenesisLtd/mathjson-solver/tree/1.x).

Version 2.0.0's only breaking change is `Log`: pre-2.0.0 it was always natural log, `["Log", x]` == `math.log(x)`. From 2.0.0 on it matches [CortexJS](https://cortexjs.io/compute-engine/) — `["Log", x]` is log base 10, `["Log", x, b]` is log base `b` — and natural log moved to `Ln`.

If you have existing expressions built for 1.x and don't want to hand-edit every `Log` node just to pick up functions added in 2.x (`Product`, the CortexJS forms of `If`/`Map`/`Filter`/`Reduce`, the new aliases, etc.), pass `legacy_v1=True` when creating the solver. It rewrites every `["Log", x]` to `["Ln", x]` before evaluating, so old expressions keep producing the same results without modification:

```python
solver = create_solver(parameters, legacy_v1=True)
solver(["Log", 8])  # 2.0794... (natural log, matching pre-2.0.0 behavior)
```

You can also run the rewrite yourself and inspect or store the translated expression:

```python
from mathjson_solver import translate_v1_mathjson

translate_v1_mathjson(["Add", ["Log", 8], 1])  # ["Add", ["Ln", 8], 1]
```

`legacy_v1=True` only affects `Log`. Every other 1.x expression already evaluates identically on 2.x without any translation.

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

## Related Projects

We also created [`londec`](https://pypi.org/project/londec/) — evaluate tree-structured conditions against an ordered history of events. It uses mathjson-solver internally.

## License

[View license information](https://github.com/LongenesisLtd/mathjson-solver/blob/main/LICENSE)

## References

This library implements the [MathJSON](https://cortexjs.io/mathjson/) format as defined by the [CortexJS Compute Engine](https://cortexjs.io/compute-engine/). Since 2.0.0, mathjson-solver has been steering towards greater compatibility with CortexJS's calling conventions and function set — while remaining an independent Python implementation, not a port or dependency of CortexJS.

**Scope:** mathjson-solver targets compatibility with CortexJS's array-form calling conventions and standard function names — not the full [Compute Engine](https://cortexjs.io/compute-engine/), which is a symbolic CAS.

---

Made with ❤️ by [Longenesis](https://longenesis.com/team)
