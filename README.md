# MathJSON Solver

[![PyPI](https://img.shields.io/pypi/v/mathjson-solver.svg)](https://pypi.org/project/mathjson-solver/)
[![PyPI Downloads](https://static.pepy.tech/badge/mathjson-solver/month)](https://pepy.tech/projects/mathjson-solver)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

> **Heads up:** Version 2 introduces a breaking change (see [CHANGELOG.md](CHANGELOG.md)) as part of steering back towards greater compatibility with [CortexJS MathJSON](https://cortexjs.io/compute-engine/): `Log` is now log base 10 instead of natural log. Stuck on pre-2.0.0 expressions but want the functions added in 2.x? Pass `legacy_v1=True` to `create_solver()` (see [Migrating from 1.x](#migrating-from-1x)) instead of hand-migrating every expression. Bugfix releases for the 1.x line also continue on the [`1.x` branch](https://github.com/LongenesisLtd/mathjson-solver/tree/1.x).

A reliable Python library for numerically evaluating mathematical expressions in MathJSON format. Perfect for applications that need to safely execute user-provided formulas, calculate dynamic equations, or process mathematical data.

**What is MathJSON?** MathJSON represents mathematical expressions as JSON arrays, like `["Add", 1, 2, 3]` for 1+2+3. This format is safe, structured, and easy to generate programmatically.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Migrating from 1.x](#migrating-from-1x)
- [Restricting Available Functions](#restricting-available-functions)
- [Supported Operations](#supported-operations)
- [Error Handling](#error-handling)
- [Use Cases](#use-cases)
- [Testing](#testing)
- [Community](#community)
- [Contributing](#contributing)
- [Related Projects](#related-projects)

## Installation

```bash
pip install mathjson-solver
```

**Requirements:** Python 3.10+

**Optional:**
- `pip install mathjson-solver[integration]` (installs numpy; only required for `TrapezoidalIntegrate`)
- `pip install mathjson-solver[regex]` (installs [google-re2](https://pypi.org/project/google-re2/); only required for `RegExp`/`IsMatch`/`StringMatch`/`StringMatchAll`)

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

## Migrating from 1.x

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

## Supported Operations

The library supports a comprehensive set of mathematical operations:

* **Arithmetic:** Add, Sum, Subtract, Multiply, Divide, Negate, Power, Square, Root, Sqrt, Abs, Round, Floor, Ceil
* **Trigonometry:** Sin, Cos, Tan, Arcsin, Arccos, Arctan, Arctan2, Cot, Sec, Csc (+ inverses), Sinh, Cosh, Tanh, Coth, Sech, Csch (+ inverses), Hypot, Sinc
* **Logarithms:** Log (base 10, or base b), Log2/Lb, Log10/Lg, Ln (natural log), LogOnePlus, Exp
* **Comparison:** Equal, StrictEqual, IdenticallyEqual, NotEqual, Greater, GreaterEqual, Less, LessEqual, Congruent
* **Logic & Sets:** Any, All, Not, And, Or, Xor, Nand, Nor, Implies, Equivalent, In/Element, NotIn/NotElement, ContainsAnyOf, ContainsAllOf, ContainsNoneOf, bare `True`/`False` literals, Union, Intersection, SetMinus, SymmetricDifference (over arrays - no dedicated Set type)
* **Statistics:** Average/Mean, Max, Min (both list and variadic forms), Median, Mode, Variance, StandardDeviation, PopulationVariance, PopulationStandardDeviation, Quartiles, InterquartileRange, Covariance, Correlation, Skewness, Kurtosis, LinearRegression, PolynomialFit, Length/Count
* **Functional Programming:** Map/StrictMap, Reduce, Filter, Product (all also accept CortexJS calling conventions, including `Function` lambdas)
* **Arrays:** Array/List creation, GenerateRange, Range, AtIndex, At, Slice, Appended/Append, First, Second, Third, Last, Rest, Most, Reverse, Sort, Unique, Dedup, Join, Zip, IsEmpty, CumulativeSum, CumulativeProduct, Take, Drop, TakeWhile, DropWhile, Contains, IndexOf, IndexWhere, Find, CountIf, Position, RotateLeft, RotateRight, MaxBy, MinBy, ArgMax, ArgMin, Ordering, FlatMap, Scan, Differences, Fold, Insert, DeleteAt, ReplaceAt, Partition, Chunk, GroupBy, ChunkBy, Tally
* **Control Flow:** If statements (Python pair form and CortexJS flat form), Switch/StrictSwitch (value-equality case dispatch), Which (CortexJS flat condition/value chain), Constants definition
* **Type Conversion:** Int, Float, Str, IsDefined
* **Strings:** String, StringJoin, ToUpperCase, ToLowerCase, CaseFold, Trim, TrimStart, TrimEnd, StringSplit, StringReplace, StringCompare, StringRepeat, PadStart, PadEnd, Characters/GraphemeClusters, Utf8, Utf16, UnicodeScalars, StringFrom, IntegerString, DigitsFrom, NumberFrom
* **Pattern Matching (requires the optional `regex` extra, `pip install mathjson-solver[regex]`):** RegExp, IsMatch, StringMatch, StringMatchAll — backed by [RE2](https://github.com/google/re2) rather than Python's `re`, for a hard guarantee against catastrophic backtracking (no backreferences/lookaround, as a deliberate trade-off for that guarantee)
* **Date/Time:** Strptime, Strftime, Today, Now, TimeDelta functions (Weeks, Days, Hours, Minutes)
* **Number Theory:** Chop, Mod, Clamp, GCD, LCM, Factorial, Binomial, IsPrime, Erf, Erfc, Rational, Numerator, Denominator, MachineEpsilon, CatalanConstant, EulerGamma, PowerMod, ModularInverse, IntegerSqrt, FactorInteger, PrimeFactors, PrimeNu, PrimeOmega, Radical, IsSquareFree, Divisors, Sigma0, Sigma1, SigmaMinus1, DivisorSigma, Divides, Totient, IsPerfectPower, NthPrime, NextPrime, PrimePi, ExtendedGCD, ChineseRemainder, CarmichaelLambda, JacobiSymbol, LegendreSymbol, MultiplicativeOrder, PrimitiveRoot, LucasL, CatalanNumber, BernoulliB, ContinuedFraction, FromContinuedFraction, IntegerDigits, DigitCount, DigitSum, FromDigits, IsSquare, IsTriangular, IsPentagonal, IsOctahedral, IsCenteredSquare, IsPerfect, IsAbundant, IsHappy
* **Special Functions:** Gamma, GammaLn, Beta, Factorial2, ErfInv, LambertW, AGM, EllipticK, EllipticE
* **Combinatorics:** Choose, Fibonacci, Multinomial, Subfactorial, BellNumber, PowerSet, Permutations, Combinations, CartesianProduct (the last four have no output-size limit - see [Restricting Available Functions](#restricting-available-functions))
* **Core (structural introspection):** Head, Tail, Hold, Identity, Type, IsSame, Same
* **Integration (requires the optional `integration` extra, `pip install mathjson-solver[integration]`):** TrapezoidalIntegrate. Also in this group but with no extra dependency: Interp, FindIntervalIndex, Variable references
* **Advanced:** HasMatchingSublist for pattern matching
* **Constants:** Pi, Degrees, ExponentialE, GoldenRatio

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

## Related Projects

We also created [`londec`](https://pypi.org/project/londec/) — evaluate tree-structured conditions against an ordered history of events. It uses mathjson-solver internally.

## License

[View license information](https://github.com/LongenesisLtd/mathjson-solver/blob/main/LICENSE)

## References

This library implements the [MathJSON](https://cortexjs.io/mathjson/) format as defined by the [CortexJS Compute Engine](https://cortexjs.io/compute-engine/). Since 2.0.0, mathjson-solver has been steering towards greater compatibility with CortexJS's calling conventions and function set — while remaining an independent Python implementation, not a port or dependency of CortexJS.

**Scope:** mathjson-solver targets compatibility with CortexJS's array-form calling conventions and standard function names — not the full [Compute Engine](https://cortexjs.io/compute-engine/), which is a symbolic CAS.

---

Made with ❤️ by [Longenesis](https://longenesis.com/team)
