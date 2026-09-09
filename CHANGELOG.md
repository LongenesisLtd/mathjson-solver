# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.2.1] - 2026-09-09

### Fixed

- **`Which` was aliased to the wrong construct.** It previously pointed at `Switch` (value-equality dispatch: `["Switch", expr, default, [case, val], ...]`), but CortexJS `Which` is a flat condition/value chain, `["Which", cond1, val1, cond2, val2, ...]`, equivalent in spirit to `If`'s pair form. `Which` now has its own implementation matching that signature, evaluating each `cond` in order and returning the `val` paired with the first truthy one, or `None` (CortexJS `Nothing`) if none match. This corrects silently-wrong results for any real CortexJS `Which` expression; if you were relying on the old `Switch`-shaped behavior, switch to `["Switch", ...]` directly.
- **`requires-python` was stale.** It claimed `>=3.6`, but the code has used a bare `X | Y` union type annotation (no `from __future__ import annotations`) since before this release - that syntax needs Python 3.10+ and fails at import time on anything older - and CI has only ever tested 3.10/3.12. Corrected to `>=3.10` to match what's actually required and tested.

### Added

- **Bare `True`/`False` boolean literals.** CortexJS represents booleans as the symbols `"True"`/`"False"` (as opposed to native JSON `true`/`false`, which already evaluated correctly as Python `bool`, itself a `numbers.Number` subtype). These symbols now resolve to actual booleans - e.g. `["Equal", "flag", "True"]` compares against boolean `True` instead of the literal string `"True"`. They're treated as reserved literals: a solver parameter or local variable named `"True"`/`"False"` can no longer shadow them, and `extract_variables` no longer reports them as free variables to supply.
- **CortexJS collection functions**, all operating on the existing `Array` representation and, where they take a function/predicate argument, accepting both the call-template and `Function`-lambda conventions already used by `Map`/`Filter`/`Reduce`:
  - Slicing: `Take`, `Drop`, `TakeWhile`, `DropWhile`
  - Searching: `Contains`, `IndexOf`, `IndexWhere`, `Find`, `CountIf`, `Position`
  - Reordering: `RotateLeft`, `RotateRight`, `MaxBy`, `MinBy`, `ArgMax`, `ArgMin`, `Ordering`
  - Transforming: `FlatMap`, `Scan`, `Differences`, `Fold` (function-first `Reduce`), `Dedup` (consecutive-only, unlike the existing `Unique`)
  - Editing: `Append` (alias for the existing `Appended`), `Insert`, `DeleteAt`, `ReplaceAt`
  - Grouping: `Partition` (fixed chunk size), `Chunk` (fixed group count), `GroupBy`, `ChunkBy`, `Tally`

  Deliberately not included in this pass: the lazy/lookup-table collection types (`Set`, `Tuple`, `Dictionary`), which would need new data types rather than fitting the existing `Array` shape, and anything requiring unbounded iteration (`Cycle`, `Iterate`, arbitrary-size `Repeat`/`Linspace`/`Tabulate`), which is out of scope for a safe evaluator of untrusted expressions.
- **Basic set algebra**, operating on the `Array` representation directly rather than requiring a dedicated `Set` type: `Union` and `Intersection` (variadic, deduplicated, order-preserving), `SetMinus` and `SymmetricDifference` (binary). Also `Element`/`NotElement`, CortexJS's names for the existing `In`/`Not_in` (`["Element", value, collection]`, matching mathematical `x ∈ S` order). Domain-membership sets (`RealNumbers`, `Integers`, etc.) and the rest of the `Set` reference page remain out of scope, as they need real domain-typing machinery, not just list operations.
- **`Second`, `Third`**: fixed-position element access alongside the existing `First`/`Last`.
- **Missing constants:** `MachineEpsilon` (`sys.float_info.epsilon`), `CatalanConstant`, `EulerGamma`.
- **Stricter/modular relations:** `IdenticallyEqual` (like `StrictEqual`, but also requires the same Python type - `1` and `1.0` are `StrictEqual` but not `IdenticallyEqual`), `Congruent` (`["Congruent", a, b, modulus]`, i.e. `a ≡ b (mod modulus)`).
- **`Rational`, `Numerator`, `Denominator`.** This solver has no dedicated rational-number type carried through arithmetic - everything downstream of `Rational` is a plain float, same as `Divide`. `Numerator`/`Denominator` read their argument's declared `n`/`d` exactly when it's an unevaluated `["Rational", n, d]` expression; otherwise (a plain number) they fall back to reconstructing the closest fraction with a bounded denominator via `fractions.Fraction` - a best-effort approximation, not exact/symbolic.
- **More statistics:** `Mode`, `PopulationVariance`, `PopulationStandardDeviation`, `Quartiles`, `InterquartileRange`, `Covariance`, `Correlation` - all thin wrappers around `statistics.mode`/`pvariance`/`pstdev`/`quantiles`/`covariance`/`correlation`, same pattern as the existing `Variance`/`StandardDeviation`.

[2.2.1]: https://github.com/LongenesisLtd/mathjson-solver/compare/v2.2.0...v2.2.1

## [2.2.0] - 2026-09-08

### Added

- **Migration helper for 1.x users:** `translate_v1_mathjson(expr)` rewrites the one breaking change from 2.0.0 (`["Log", x]`, previously natural log) to its 2.x equivalent (`["Ln", x]`), leaving everything else untouched. `create_solver(parameters, legacy_v1=True)` applies this automatically, so existing 1.x expressions keep evaluating to the same results on 2.x without hand-editing, while still gaining access to functions added in 2.x.

[2.2.0]: https://github.com/LongenesisLtd/mathjson-solver/compare/v2.1.1...v2.2.0

## [2.1.1] - 2026-08-19

### Fixed

- Fixed packaging: the sdist now only includes the intended package, tests, docs, and metadata files.

[2.1.1]: https://github.com/LongenesisLtd/mathjson-solver/compare/v2.1.0...v2.1.1

## [2.1.0] - 2026-08-19

Continues the CortexJS compatibility pass: `If`, `Map`, `Filter`, and `Reduce` now also accept CortexJS calling conventions, alongside the existing Python-specific forms.

### Fixed

- **Correctness fix:** a locally-bound name (a `Constants` binding, a `Reduce` accumulator/current/index variable, or a `Function` parameter, see below) now correctly shadows a top-level solver parameter of the same name, instead of the global value silently winning. Previously `create_solver({"x": 5})` evaluating `["Constants", ["x", 100], ["Add", "x", 1]]` returned `6` instead of `101`. If you were unknowingly relying on the old (backwards) precedence, this will change your result.

### Added

- **`Function`**: now a real CortexJS-style lambda, `["Function", body, param1, param2, ...]`. With no parameter names, `body` can reference its arguments via the anonymous placeholders `"_"` (first argument only) and `"_1"`, `"_2"`, ... Meant to be passed as the function argument to `Map`, `Filter`, and `Reduce`; evaluated on its own it returns unevaluated. (Previously a non-functional stub that always returned `0`.)
- **`If`**: now also accepts the CortexJS flat form, `["If", cond, then]` / `["If", cond, then, else]`, including the no-else form (returns `None`/CortexJS `Nothing` when the condition is false). The existing Python pair form, `["If", [cond, val], ..., else_val]`, is unchanged and detected automatically. (Note: a Python-form condition that is a bare parameter reference, e.g. `["If", ["my_flag", "yes"], "no"]`, is still correctly disambiguated — but wrapping such conditions in `IsTrue`/`IsFalse` remains the clearer style.)
- **`Map` / `StrictMap` / `Filter`**: the function argument can now be a `["Function", ...]` expression (see above), in addition to the existing call-template form (e.g. `["Square"]`).
- **`Reduce`**: now also accepts the CortexJS form, `["Reduce", collection, fn]` / `["Reduce", collection, fn, initial]`, where `fn` is applied as `fn(accumulator, current_item)` (call-template or `Function` form). Without an initial value, the first element seeds the accumulator. The existing 6-argument Python form (with named accumulator/current/index variables) is unchanged and detected automatically via argument count.
- **`Product`**: `["Product", array]` multiplies together the numeric elements of `array`.

[2.1.0]: https://github.com/LongenesisLtd/mathjson-solver/compare/v2.0.0...v2.1.0

## [2.0.0] - 2026-08-19

Steers the solver back towards greater compatibility with [CortexJS MathJSON](https://cortexjs.io/compute-engine/), adding aliases and constructs that were previously CortexJS-only.

### Changed

- **BREAKING:** `Log` now matches CortexJS: `["Log", x]` is log base 10, and `["Log", x, b]` is log base `b`. Previously `Log` was natural log; use `Ln` for that.
- `Max` and `Min` now also accept a variadic (CortexJS) form, e.g. `["Max", 5, 2, -1]`, in addition to the existing single-array form.

### Added

- CortexJS aliases: `Lb` (`Log2`), `Lg` (`Log10`), `List` (`Array`), `Mean` (`Average`), `Count` (`Length`), `Which` (`Switch`).
- New math functions: `LogOnePlus`, `Chop`, `Mod`, `Clamp`, `GCD`, `LCM`, `Factorial`, `Binomial`, `IsPrime`, `Erf`, `Erfc`.
- New logic functions: `Xor`, `Nand`, `Nor`, `Implies`, `Equivalent`.
- New trigonometric functions: `Arctan2`, `Cot`, `Sec`, `Csc`, `Arccot`, `Arcsec`, `Arccsc`, `Sinh`, `Cosh`, `Tanh`, `Coth`, `Sech`, `Csch`, `Arsinh`, `Arcosh`, `Artanh`, `Arcoth`, `Arsech`, `Arcsch`, `Hypot`, `Sinc`.
- New constants: `Degrees`, `ExponentialE`, `GoldenRatio`.
- New statistics: `Variance`, `StandardDeviation`.
- New array/collection functions: `First`, `Last`, `Rest`, `Most`, `Reverse`, `Sort`, `IsEmpty`, `Range` (CortexJS-compatible, distinct from `GenerateRange`), `Join`, `Unique`, `Zip`, `At` (1-indexed, distinct from `AtIndex`).

[2.0.0]: https://github.com/LongenesisLtd/mathjson-solver/compare/v1.20.2...v2.0.0

## [1.20.2] - 2026-08-18

### Fixed

- Fix `extract_variables` for Constants (thanks [@nkimdwave](https://github.com/nkimdwave)!)
- Add missing functions to constructs in `extract_variables` (thanks [@nkimdwave](https://github.com/nkimdwave)!)

[1.20.2]: https://github.com/LongenesisLtd/mathjson-solver/compare/461bc00...v1.20.2
