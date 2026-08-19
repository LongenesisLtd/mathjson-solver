# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
