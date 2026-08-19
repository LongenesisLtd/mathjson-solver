# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
