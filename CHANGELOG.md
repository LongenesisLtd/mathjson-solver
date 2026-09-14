# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.3.0] - Unreleased

### Changed

- The evaluator no longer copies its whole variable scope on every recursive evaluation step - only the constructs that actually introduce a new binding (`Constants`, `Reduce`'s legacy accumulator form, `TrapezoidalIntegrate`) copy it, and only their own copy. Measured 2-3x faster on arithmetic- and `Reduce`-heavy expressions; no behavior change.

### Fixed

- **`extract_variables` treated unrecognized constructs' arguments as free variables.** `["Color", "red"]` would report `"red"` as a parameter to supply, even though it's a literal argument to a construct this solver doesn't implement - not a variable reference. `extract_variables` now mirrors `f()`'s own fallback for an unrecognized construct (return the expression unchanged, never evaluating or substituting into its arguments): it's treated as opaque data, contributing no free variables, rather than recursed into. Applies to any unimplemented construct (`Color`, `Quantity`, etc.), not just specific names. The same treatment was extended to `Head`/`Tail`/`Hold`/`IsSame`/`Same` (new in this release, see below), which likewise never evaluate their arguments.

### Added

- **More statistics:** `Skewness`, `Kurtosis` (sample-adjusted, matching Excel's `SKEW`/`KURT` and `scipy.stats.skew`/`kurtosis` with `bias=False`), `LinearRegression` (least-squares fit, returns `["Array", slope, intercept]`), `PolynomialFit` (least-squares fit of a given degree via the normal equations, no numpy dependency, returns `["Array", c0, c1, ..., cd]` - lowest degree first, the opposite order from `numpy.polyfit`). `PolynomialFit`'s degree is capped at 50.
- **Number theory**, ~45 new functions:
  - stdlib-based: `PowerMod`, `ModularInverse`, `IntegerSqrt`
  - Factorization: `FactorInteger`, `PrimeFactors`, `PrimeNu`, `PrimeOmega`, `Radical`, `IsSquareFree`
  - Divisors: `Divisors`, `Sigma0`, `Sigma1`, `SigmaMinus1`, `DivisorSigma`, `Divides`, `Totient`, `IsPerfectPower`
  - Prime lookups (capped - `NthPrime`'s `n`/`NextPrime`'s `k` at 10,000, `NextPrime`'s starting value and every factorization-based function above at `10**12`, `PrimePi`'s `n` at 100,000; picked from measured worst-case timing, not guessed): `NthPrime`, `NextPrime`, `PrimePi`
  - Modular structure: `ExtendedGCD`, `ChineseRemainder`, `CarmichaelLambda`, `JacobiSymbol`, `LegendreSymbol`, `MultiplicativeOrder`, `PrimitiveRoot`
  - Sequences: `LucasL`, `CatalanNumber`, `BernoulliB` (exact, via `fractions.Fraction`; uses the B₁ = -1/2 convention), `ContinuedFraction`, `FromContinuedFraction`
  - Digit manipulation (array form, alongside the existing string-based `IntegerString`/`DigitsFrom`): `IntegerDigits`, `DigitCount`, `DigitSum`, `FromDigits`
  - Figurate numbers and predicates: `IsSquare`, `IsTriangular`, `IsPentagonal`, `IsOctahedral`, `IsCenteredSquare`, `IsPerfect`, `IsAbundant`, `IsHappy`

  Not included: `RandomPrime` (nondeterminism, same reasoning as `Random`/`RandomChoice`/`RandomSample`).
- **Special functions:** `Gamma`, `GammaLn` (`math.gamma`/`math.lgamma`), `Beta`, `Factorial2`, and verified iterative algorithms `ErfInv`, `LambertW`, `AGM`, `EllipticK`, `EllipticE` (the "parameter" convention `K(m)`/`E(m)`, `m = k²`), `Hypergeometric1F1`, `Hypergeometric2F1` (defining power series; `Hypergeometric1F1` capped at `|z| <= 500` and uses Kummer's transformation for `z < 0` to avoid catastrophic cancellation, `Hypergeometric2F1` restricted to `|z| < 1`, its actual radius of convergence). Not included: `JacobiTheta`, `DedekindEta` - `scipy.special` (see below) doesn't implement these either, so they'd need a from-scratch q-series with the same "subtly wrong across the domain" risk as any other naive truncated series.
- **`BesselJ`/`BesselY`/`BesselI`/`BesselK`, `AiryAi`/`AiryBi`/`AiryAiPrime`/`AiryBiPrime`, `Zeta`, `GammaRegularized`, `BetaRegularized`** - thin wrappers around `scipy.special`, behind a new optional `special-functions` extra (`pip install mathjson-solver[special-functions]`), same pattern as `integration`/`regex`. `GammaRegularized(a, z)` is the *upper* regularized incomplete gamma (`scipy`'s own `gammainc` is the lower form; this uses `gammaincc`); `BetaRegularized(x, a, b)` puts `x` first, unlike `scipy.special.betainc`'s `(a, b, x)`. Without the extra installed, these raise a clear `ImportError` naming the missing package.
- **Combinatorics:** `Choose` (alias for `Binomial`), `Fibonacci`, `Multinomial`, `Subfactorial`, `BellNumber`, and the enumeration functions `PowerSet`, `Permutations`, `Combinations`, `CartesianProduct` - the latter four have **no built-in output-size limit** (a set of `n` elements has `2^n` subsets, etc.); see the new `blacklist` parameter below for disabling them in deployments that accept untrusted expressions.
- **Core (structural introspection):** `Head`/`Tail` (operator name / argument list of a compound expression, read from the raw unevaluated tree), `Hold` (returns an argument unevaluated), `Identity`, `Type` (runtime kind of an evaluated value), `IsSame`/`Same` (structural, pre-evaluation equality - distinct from `Equal`/`StrictEqual`/`IdenticallyEqual`, which all compare evaluated values). Not included: CAS functions (`Evaluate`, `Expand`, `Simplify`, `Solve`, ...), mutable-state functions (`Declare`, `Assign`, `Assume`, ...), and LaTeX serialization (`Parse`, `Latex`, `Subscript`, ...) - same reasoning as elsewhere in this solver (no CAS, no mutable state, no rendering surface). `Error`/`IsError` also not included - this solver already has an established, different error model (`MathJSONException`).
- **`create_solver(parameters, blacklist=[...])`**: disables the named constructs for that solver instance, raising `MathJSONException` if an expression tries to use one, rather than evaluating it or silently ignoring it. An access-policy control, not a resource limiter - it doesn't make an enabled construct safe against pathological input (in particular, it's the recommended way to disable the four uncapped enumeration functions above for untrusted expression sources). A blacklisted name that isn't an actual construct has no effect (not validated against the known-construct list).
- **Type hints on the public API**: `create_solver`, `MathJSONException`, `extract_variables`, `translate_v1_mathjson` now have accurate parameter/return type hints, built on one shared `MathJSONExpression` alias for a MathJSON node (`str | int | float | bool | None | list[MathJSONExpression]`). The ~300 per-construct functions inside `create_solver`'s closure remain untyped - they operate on arbitrary runtime values by design (a construct can produce a `Fraction`, a `datetime.timedelta`, a compiled regex pattern, ...), so annotating each one wouldn't add real type safety.

## [2.2.1] - 2026-09-14

### Fixed

- **`Which`** was aliased to `Switch` (value-equality dispatch: `["Switch", expr, default, [case, val], ...]`) instead of implementing CortexJS's actual flat condition/value chain, `["Which", cond1, val1, cond2, val2, ...]`. It now evaluates each `cond` in order and returns the `val` paired with the first truthy one, or `None` (CortexJS `Nothing`) if none match. If you were relying on the old `Switch`-shaped behavior, use `["Switch", ...]` directly.
- **`requires-python`** claimed `>=3.6`; the codebase has required Python 3.10 since before this release (a bare `X | Y` union type annotation with no `from __future__ import annotations`, which fails at import time on older versions), and CI has only ever tested 3.10/3.12. Corrected to `>=3.10`. The README's "Requirements: Python 3.7+" had the same problem and is corrected too.
- **`numpy`** is now declared as a proper optional extra (`integration = ["numpy"]` in `pyproject.toml`, `pip install mathjson-solver[integration]`) instead of an undeclared `try/except ImportError` dependency, and is installed in CI so `TrapezoidalIntegrate`'s tests run there.

### Added

- **Bare `True`/`False` boolean literals** - CortexJS's boolean symbols (native JSON `true`/`false` already worked). Reserved: a solver parameter or local variable of the same name can't shadow them.
- **CortexJS collection functions**, all operating on `Array` and, where they take a function/predicate argument, accepting both the call-template and `Function`-lambda conventions already used by `Map`/`Filter`/`Reduce`:
  - Slicing: `Take`, `Drop`, `TakeWhile`, `DropWhile`
  - Searching: `Contains`, `IndexOf`, `IndexWhere`, `Find`, `CountIf`, `Position`
  - Reordering: `RotateLeft`, `RotateRight`, `MaxBy`, `MinBy`, `ArgMax`, `ArgMin`, `Ordering`
  - Transforming: `FlatMap`, `Scan`, `Differences`, `Fold` (function-first `Reduce`), `Dedup` (consecutive-only, unlike `Unique`)
  - Editing: `Append` (alias for the existing `Appended`), `Insert`, `DeleteAt`, `ReplaceAt`
  - Grouping: `Partition` (fixed chunk size), `Chunk` (fixed group count), `GroupBy`, `ChunkBy`, `Tally`
- **Basic set algebra** over `Array`: `Union` and `Intersection` (variadic, deduplicated, order-preserving), `SetMinus`, `SymmetricDifference`, and `Element`/`NotElement` (CortexJS's names for the existing `In`/`Not_in`).
- **`Second`, `Third`**: fixed-position element access alongside `First`/`Last`.
- **New constants:** `MachineEpsilon`, `CatalanConstant`, `EulerGamma`.
- **New relations:** `IdenticallyEqual` (like `StrictEqual`, but also requires the same Python type - `1` and `1.0` are `StrictEqual` but not `IdenticallyEqual`), `Congruent` (`["Congruent", a, b, modulus]`, i.e. `a ≡ b (mod modulus)`).
- **`Rational`, `Numerator`, `Denominator`.** `Rational(n, d)` evaluates to `n / d` (this solver has no rational-number type carried through arithmetic). `Numerator`/`Denominator` read a `Rational` node's declared `n`/`d` exactly when passed one directly; otherwise they reconstruct an approximate fraction from the numeric value.
- **More statistics:** `Mode`, `PopulationVariance`, `PopulationStandardDeviation`, `Quartiles`, `InterquartileRange`, `Covariance`, `Correlation`.
- **String functions:** `String`, `StringJoin`, `ToUpperCase`, `ToLowerCase`, `CaseFold`, `Trim`/`TrimStart`/`TrimEnd`, `StringSplit`, `StringReplace` (literal substring, not pattern-based), `StringCompare`, `Characters`/`GraphemeClusters` (Unicode code points, not full grapheme clusters), `Utf8`/`Utf16`/`UnicodeScalars` and their inverse `StringFrom`, `IntegerString`/`DigitsFrom` (base 2-36), `NumberFrom`. `StringRepeat`/`PadStart`/`PadEnd` are capped at 100,000 characters. `Join` stays `Array`-only (unlike CortexJS's polymorphic `Join`); `StringJoin` is the dedicated string name.
- **Pattern matching: `RegExp`, `IsMatch`, `StringMatch`, `StringMatchAll`**, backed by [RE2](https://github.com/google/re2) rather than Python's `re`, for a hard guarantee against catastrophic backtracking (ReDoS) - at the cost of no backreferences or lookahead/lookbehind. Requires the new `regex` extra: `pip install mathjson-solver[regex]` (installs [`google-re2`](https://pypi.org/project/google-re2/)). `RegExp` compiles a pattern (optional `i`/`m`/`s` flags) into a reusable value; `IsMatch`/`StringMatch`/`StringMatchAll` accept that value or a bare pattern string. `StringMatch`/`StringMatchAll` return `["Array", matched_text, start, end, ["Array", group, ...]]` per match (1-indexed `start`, exclusive `end`, matching this solver's other index conventions).

Not included: `Delimiter`, `Spacing`, `Annotated`, `Text`, `BaseForm` (LaTeX-rendering hints, not applicable to a headless evaluator); `Set`, `Tuple`, `Dictionary`, and unbounded-iteration collections (`Cycle`, `Iterate`, arbitrary-size `Repeat`/`Linspace`/`Tabulate`); domain-membership sets (`RealNumbers`, `Integers`, etc.).

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
