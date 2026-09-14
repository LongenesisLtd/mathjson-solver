# MathJSON Solver Documentation

## Table of Contents

1. [Basic Arithmetic](#basic-arithmetic)
2. [Mathematical Functions](#mathematical-functions)
3. [Number Theory](#number-theory)
4. [Special Functions](#special-functions)
5. [Combinatorics](#combinatorics)
6. [Core](#core)
7. [Comparison Operations](#comparison-operations)
8. [Control Flow](#control-flow)
9. [Arrays and Aggregation](#arrays-and-aggregation)
10. [Boolean and Set Operations](#boolean-and-set-operations)
11. [Type Conversion](#type-conversion)
12. [Date and Time Functions](#date-and-time-functions)
13. [Trigonometric Functions](#trigonometric-functions)
14. [Advanced Functions](#advanced-functions)
15. [String Functions](#string-functions)
16. [Pattern Matching](#pattern-matching)
17. [Integration Functions](#integration-functions)

---

## Basic Arithmetic

### Add
`Add` iteratively adds up the given values. Compatible with time delta. It is intended that supporting expression builders render `["Add", 2, 4, 3]` as _2+4+3_.

```python
["Add", 2, 4, 3]                  # 2+4+3=9
```

`Add` is intentionally forgiving as it tries to convert strings to numbers, making addition of strings like `["Add", "2", "4", "3"]` actually possible. Also, it ignores un-convertible elements so arrays like `["Add", "2", "three", "4", "6"]` don't crash the solver.

`Add` does not work with nested arrays.

```python
["Add", 2, 4, 3]                  # 2+4+3=9
["Add", 2, 4, "3"]                # 2+4+3=9
["Add", 2, 4, "3", None]          # 2+4+3=9
["Add", 2, 4, "3", None, "abc"]   # 2+4+3=9
```

### AddScalar
Adds a scalar value to each element of an array.

```python
["AddScalar", ["Array", 2, 3, 4], 1]                 # ["Array", 3, 4, 5]
```

### AddArray
Performs element-wise addition between two arrays of equal length.

```python
["AddArray", ["Array", 2, 3, 4], ["Array", 1, 2, 3]]  # ["Array", 3, 5, 7]
```

### Sum
Adds up the given values. `Sum` internally uses `Add` function. Compatible with nested arrays. It is intended that supporting expression builders render `["Sum", 2, 4, 3]` as _∑(2, 4, 3)_.

```python
["Sum", 2, 4, 3]                  # ∑(2, 4, 3)=9
```

### Negate
Inverts the sign.

```python
["Negate", 3]                     # -(3)=-3
["Negate", -3]                    # -(-3)=3
["Add", 5, 4, ["Negate", 3]]      # 5+4+(-3)=6
```

### Subtract
Performs basic subtraction.

```python
["Subtract", 10, 5, 2]            # 10-5-2=3
```

### SubtractScalar
Subtracts a scalar value from each element of an array.

```python
["SubtractScalar", ["Array", 2, 3, 4], 1]            # ["Array", 1, 2, 3]
```

### SubtractArray
Performs element-wise subtraction between two arrays of equal length.

```python
["SubtractArray", ["Array", 2, 3, 4], ["Array", 1, 2, 7]]  # ["Array", 1, 1, -3]
```

### Multiply
Performs basic multiplication.

```python
["Multiply", 2, 4]                # 2*4=8
["Multiply", 2, 3, 4]             # 2*3*4=24
```

### MultiplyByScalar
Multiplies each element of an array by a scalar value.

```python
["MultiplyByScalar", ["Array", 2, 3, 4], 5]           # ["Array", 10, 15, 20]
```

### MultiplyByArray
Performs element-wise multiplication between two arrays of equal length.

```python
["MultiplyByArray", ["Array", 2, 3, 4], ["Array", 1, 2, 3]]  # ["Array", 2, 6, 12]
```

### Divide
Performs division between two numbers. Always returns a floating-point result.

```python
["Divide", 10, 5]                 # 10/5=2.0
["Divide", 10, 4]                 # 10/4=2.5
["Divide", 1, 3]                  # 1/3=0.33333333333...
```

`Divide` can be used in complex expressions:

```python
["Divide", 10, ["Add", 2, 3]]     # 10/(2+3)=10/5=2.0
```

**Exception Handling:**
Division by zero raises a `MathJSONException`:

```python
["Divide", 1, 0]                  # Raises: MathJSONException: Problem in Divide. ['Divide', 1, 0]. division by zero
```

---

## Mathematical Functions

### Power and Square
`Power` raises a number to given power. `Square` is a special case of `Power`.

```python
["Power", 2, 3]                   # 2^3=8
["Square", 4]                     # 4^2=16
```

### Root and Square Root

```python
["Root", 9, 2]                    # √9=3.0
["Root", 8, 3]                    # ∛8=2.0
["Sqrt", 9]                       # √9=3.0
```

### Exponents and Logarithms

`Log` matches [CortexJS](https://cortexjs.io/compute-engine/): with one argument it is log base 10; with a second argument it is log of that arbitrary base. For natural log, use `Ln`.

> **Breaking change (2.0.0):** `["Log", x]` previously meant natural log. If you relied on that, switch to `["Ln", x]`.

`Lb` and `Lg` are CortexJS aliases for `Log2` and `Log10` respectively. `LogOnePlus` is `ln(x + 1)`, computed with `math.log1p` for numerical stability near zero.

```python
["Exp", 2]                        # e^2≅7.389
["Log", 1000]                     # log10(1000)=3.0
["Log", 8, 2]                     # log base 2 of 8 = 3.0
["Ln", 2.7183]                    # ln(2.7183)≅1.0000
["Log2", 8]                       # log2(8)=3.0
["Log10", 1000]                   # log10(1000)=3.0
["Lb", 8]                         # log2(8)=3.0
["Lg", 1000]                      # log10(1000)=3.0
["LogOnePlus", 0]                 # ln(1+0)=0.0
```

### Absolute Value

```python
["Abs", -3.5]                     # |-3.5| = 3.5
["Abs", 3.5]                      # |3.5| = 3.5
["Abs", 0]                        # |0| = 0
```

### Rounding

```python
["Round", -5.123456, 2]           # -5.12
["Round", -5.123456, 0]           # -5.0
["Round", 5.4]                    # 5
["Round", 5.5]                    # 6
```

### Floor and Ceiling

#### Floor
Returns the largest integer less than or equal to the given number.

```python
["Floor", 4.7]                    # 4
["Floor", 4.0]                    # 4
["Floor", -2.3]                   # -3
```

#### Ceil
Returns the smallest integer greater than or equal to the given number.

```python
["Ceil", 4.1]                     # 5
["Ceil", 4.0]                     # 4
["Ceil", -2.3]                    # -2
```

### Constants

```python
["Pi"]                            # 3.141592653589793
["Multiply", 2, ["Pi"]]           # 2π ≈ 6.283
["Degrees"]                       # π/180 ≈ 0.01745 (multiply degrees by this to get radians)
["ExponentialE"]                  # e ≈ 2.71828
["GoldenRatio"]                   # φ ≈ 1.61803
["MachineEpsilon"]                # ≈ 2.22e-16 (smallest representable difference from 1.0)
["CatalanConstant"]               # ≈ 0.91597
["EulerGamma"]                    # ≈ 0.57722 (Euler-Mascheroni constant)
```

### Number Theory and Special Functions

*(The basics below have lived here since early on; the much larger
number-theory batch - factorization, modular arithmetic, prime lookups,
figurate-number predicates, and more - has its own [Number
Theory](#number-theory) section further down.)*

```python
["Chop", 1e-12]                   # 0 (values with |x| < 1e-10 collapse to 0)
["Chop", 5]                       # 5
["Mod", 7, 3]                     # 1
["Mod", -7, 3]                    # 2 (Euclidean modulus, sign matches divisor)
["Clamp", 5, 0, 3]                # 3 (bounds value between lower and upper, default -1..1)
["Clamp", -5, 0, 3]               # 0
["GCD", 12, 18]                   # 6
["LCM", 4, 6]                     # 12
["Factorial", 5]                  # 120
["Binomial", 5, 2]                # 10 (5 choose 2)
["IsPrime", 7]                    # True
["IsPrime", 8]                    # False
["Erf", 1]                        # 0.8427... (error function)
["Erfc", 1]                       # 0.1573... (complementary error function)
```

### Rational Numbers
This solver has no dedicated rational-number type carried through arithmetic - `Rational` evaluates to a plain float, same as `Divide`.

```python
["Rational", 3, 4]                # 0.75
```

`Numerator`/`Denominator` read a `["Rational", n, d]` expression's declared `n`/`d` exactly when passed one directly (unreduced - `["Rational", 6, 8]` gives numerator `6`, not `3`); otherwise (a plain number) they fall back to reconstructing the closest fraction with a bounded denominator, a best-effort approximation rather than exact/symbolic.

```python
["Numerator", ["Rational", 3, 4]]  # 3
["Denominator", ["Rational", 3, 4]]  # 4
["Numerator", 5]                   # 5 (plain integers have denominator 1)
["Denominator", 5]                 # 1
["Numerator", 0.75]                # 3 (reconstructed from the float)
["Denominator", 0.75]              # 4
```

---

## Number Theory

Several of these functions use trial division (`FactorInteger`,
`Divisors`, and everything built on them) or a forward search
(`NthPrime`, `NextPrime`, `PrimePi`) - fine for everyday integers, but
slow at very large magnitudes. Each is capped: factorization-based
functions and `NextPrime`'s starting value at `10**12`, `NthPrime`'s `n`
and `NextPrime`'s `k` at `10,000`, and `PrimePi`'s `n` at `100,000` -
picked from actual timing (worst case comfortably under half a second).

### PowerMod, ModularInverse, IntegerSqrt
Thin wrappers around Python's own `pow(a, b, m)`, `pow(a, -1, m)`, and
`math.isqrt`.

```python
["PowerMod", 4, 13, 497]           # 445
["ModularInverse", 3, 11]          # 4  (3 * 4 = 12 ≡ 1 mod 11)
["IntegerSqrt", 50]                # 7  (largest integer m with m² ≤ 50)
```

### FactorInteger, PrimeFactors, PrimeNu, PrimeOmega, Radical, IsSquareFree
All built on the same trial-division factorization. `FactorInteger`
returns `[prime, exponent]` pairs; `PrimeFactors` just the distinct
primes; `PrimeNu`/`PrimeOmega` count factors without and with
multiplicity (ω(n) and Ω(n)); `Radical` is the product of distinct
prime factors; `IsSquareFree` tests for repeated factors.

```python
["FactorInteger", 360]             # ["Array", ["Array", 2, 3], ["Array", 3, 2], ["Array", 5, 1]]
["PrimeFactors", 360]              # ["Array", 2, 3, 5]
["PrimeNu", 360]                   # 3
["PrimeOmega", 360]                # 6  (2³·3²·5¹ → 3+2+1)
["Radical", 360]                   # 30  (2·3·5)
["IsSquareFree", 360]              # False (2³·3² has repeated factors)
["IsSquareFree", 30]               # True (2·3·5, all distinct)
```

### Divisors, Sigma0, Sigma1, SigmaMinus1, DivisorSigma
`Divisors` lists all positive divisors; `Sigma0` counts them; `Sigma1`
sums them; `SigmaMinus1` sums their reciprocals (exact, via
`fractions.Fraction`); `DivisorSigma` generalizes to Σdᵏ for any `k`.

```python
["Divisors", 28]                   # ["Array", 1, 2, 4, 7, 14, 28]
["Sigma0", 28]                     # 6
["Sigma1", 28]                     # 56
["SigmaMinus1", 6]                 # 2  (1 + 1/2 + 1/3 + 1/6)
["DivisorSigma", 28, 2]            # 1050  (sum of squares of divisors)
```

### Divides and Totient
```python
["Divides", 4, 28]                 # True  (4 divides 28)
["Divides", 5, 28]                 # False
["Totient", 36]                    # 12  (Euler's φ: count of integers ≤ 36 coprime to 36)
```

### IsPerfectPower
Whether `n = a^b` for some integers `a, b ≥ 2`. Uses exact integer
roots (binary search), not floating-point `**(1/b)`, to stay correct
for large `n`.

```python
["IsPerfectPower", 27]             # True (3³)
["IsPerfectPower", 15]             # False
```

### NthPrime, NextPrime, PrimePi
`NthPrime` is 1-indexed (`NthPrime(1) = 2`). `NextPrime` finds the
smallest prime greater than `n`, or the `k`-th such prime. `PrimePi` is
the prime-counting function π(n).

```python
["NthPrime", 10]                   # 29
["NextPrime", 10]                  # 11
["NextPrime", 10, 3]               # 17  (3rd prime after 10: 11, 13, 17)
["PrimePi", 100]                   # 25  (25 primes ≤ 100)
```

### ExtendedGCD and ChineseRemainder
`ExtendedGCD` returns `["Array", gcd, x, y]` such that `a·x + b·y =
gcd(a, b)`. `ChineseRemainder` solves a system of congruences (moduli
must be pairwise coprime).

```python
["ExtendedGCD", 35, 15]            # ["Array", 5, 1, -2]  (35·1 + 15·-2 = 5)
["ChineseRemainder", ["Array", 2, 3, 2], ["Array", 3, 5, 7]]  # 23
```

### CarmichaelLambda, JacobiSymbol, LegendreSymbol, MultiplicativeOrder, PrimitiveRoot
```python
["CarmichaelLambda", 561]          # 80  (561 = 3·11·17 is the smallest Carmichael number)
["JacobiSymbol", 2, 7]             # 1
["LegendreSymbol", 3, 7]           # -1  (LegendreSymbol is JacobiSymbol restricted to a prime modulus)
["MultiplicativeOrder", 3, 7]      # 6   (3 is a primitive root mod 7)
["PrimitiveRoot", 7]               # 3   (smallest primitive root)
```

### LucasL, CatalanNumber, BernoulliB
`BernoulliB` returns exact rationals (via `fractions.Fraction`), using
the **B₁ = -1/2** convention (matching Mathematica and most modern
sources - the alternative B₁ = +1/2 convention exists too, differing
only at n=1).

```python
["LucasL", 4]                      # 7  (Lucas sequence: 2, 1, 3, 4, 7, 11, 18, ...)
["CatalanNumber", 4]               # 14
["BernoulliB", 1]                  # -1/2
["BernoulliB", 4]                  # -1/30
```

### ContinuedFraction and FromContinuedFraction
`["ContinuedFraction", x]` or `["ContinuedFraction", x, max_terms]`
(default 20). Stops early if the expansion terminates, or if a term
becomes implausibly large - past a certain point a `float`'s precision
is exhausted and further terms would just be numerical noise, not real
information about `x`. A finite continued fraction has two equally
valid representations differing only in the last term (`[..., a]` and
`[..., a - 1, 1]` are the same value); which one comes out depends on
where the expansion happens to terminate.

```python
["ContinuedFraction", 22 / 7]      # ["Array", 3, 7]
["FromContinuedFraction", ["Array", 3, 7, 15, 1]]  # 355/113 (a famous rational approximation of π)
```

### IntegerDigits, DigitCount, DigitSum, FromDigits
Siblings of [`IntegerString`/`DigitsFrom`](#integerstring-digitsfrom-numberfrom),
operating on a digit *array* instead of a string, in a given base
(default 10).

```python
["IntegerDigits", 12345]           # ["Array", 1, 2, 3, 4, 5]
["IntegerDigits", 255, 16]         # ["Array", 15, 15]
["DigitCount", 12345]              # 5
["DigitSum", 12345]                # 15
["FromDigits", ["Array", 1, 2, 3, 4, 5]]  # 12345
```

### Figurate numbers and other predicates
```python
["IsSquare", 49]                   # True
["IsTriangular", 15]               # True   (1+2+3+4+5)
["IsPentagonal", 12]               # True
["IsOctahedral", 6]                # True
["IsCenteredSquare", 13]           # True   (sequence: 1, 5, 13, 25, 41, ...)
["IsPerfect", 28]                  # True   (1+2+4+7+14 = 28)
["IsAbundant", 12]                 # True   (1+2+3+4+6 = 16 > 12)
["IsHappy", 19]                    # True   (1²+9²=82 → 8²+2²=68 → 6²+8²=100 → 1²+0²+0²=1)
["IsHappy", 4]                     # False  (cycles without reaching 1)
```

### Deliberately excluded
`RandomPrime` - same reasoning as `Random`/`RandomChoice`/`RandomSample`
throughout this solver: nondeterminism undermines reproducible formula
evaluation.

---

## Special Functions

### Gamma, GammaLn, Beta, Factorial2
`Gamma`/`GammaLn` are thin wrappers around `math.gamma`/`math.lgamma`.
`Beta` is built from `Gamma`. `Factorial2` is the double factorial
(product of integers of the same parity as `n`, down to 1 or 2).

```python
["Gamma", 5]                       # 24.0  (Gamma(n) = (n-1)! for positive integers)
["Round", ["Beta", 2, 3], 4]       # 0.0833  (Γ(2)Γ(3)/Γ(5))
["Factorial2", 7]                  # 105  (7·5·3·1)
["Factorial2", 8]                  # 384  (8·6·4·2)
```

### ErfInv, LambertW, AGM, EllipticK, EllipticE
Iterative algorithms verified against known reference values before
shipping - no new dependency needed. `EllipticK`/`EllipticE` use the
"parameter" convention `K(m)`/`E(m)` (`m = k²`), not
the "modulus" convention `K(k)`/`E(k)` some sources use, and are only
defined for `0 ≤ m ≤ 1`. `LambertW` is the principal (real) branch,
defined for `x ≥ -1/e`.

```python
["Round", ["ErfInv", 0.5], 5]      # 0.47694
["Round", ["LambertW", 1], 5]      # 0.56714  (the "Omega constant")
["Round", ["AGM", 1, 2], 5]        # 1.45679  (arithmetic-geometric mean)
["Round", ["EllipticK", 0.5], 5]   # 1.85407
["Round", ["EllipticE", 0.5], 5]   # 1.35064
```

### Hypergeometric1F1, Hypergeometric2F1
Confluent (`1F1`) and Gauss (`2F1`) hypergeometric functions, via their
defining power series - verified against `mpmath` and CortexJS's own
documented examples before shipping. `Hypergeometric1F1` is capped at
`|z| ≤ 500` (the naive series overflows a float beyond that) and uses
Kummer's transformation for `z < 0` to avoid catastrophic cancellation
that would otherwise silently corrupt the result well within that
range. `Hypergeometric2F1` only supports `|z| < 1`, its actual
mathematical radius of convergence.

```python
["Round", ["Hypergeometric1F1", 1, 2, 2], 5]        # 3.19453
["Round", ["Hypergeometric2F1", 1, 1, 2, 0.5], 5]   # 1.38629
```

### BesselJ, BesselY, BesselI, BesselK, AiryAi, AiryBi, AiryAiPrime, AiryBiPrime, Zeta, GammaRegularized, BetaRegularized
Require the optional `special-functions` extra
(`pip install mathjson-solver[special-functions]`), which installs
[scipy](https://scipy.org/) - these need real numerical algorithms
(stable series/asymptotic-expansion switching depending on argument
regime) that this project doesn't reimplement from scratch, unlike the
verified-in-house algorithms above. Thin wrappers around
`scipy.special`, verified against CortexJS's own documented examples.
Two argument-convention gotchas worth knowing, since they don't match
`scipy`'s own conventions directly:
- `GammaRegularized(a, z)` is the *upper* regularized incomplete gamma,
  `Q(a, z) = Γ(a, z) / Γ(a)` - `scipy.special.gammainc` computes the
  *lower* form (`P`); this uses `gammaincc` instead.
- `BetaRegularized(x, a, b)` puts `x` first, while
  `scipy.special.betainc` takes `(a, b, x)`.

```python
["Round", ["BesselJ", 0, 1], 4]              # 0.7652
["Round", ["AiryAi", 0], 4]                  # 0.355
["Round", ["Zeta", 2], 6]                    # 1.644934  (π²/6)
["Round", ["GammaRegularized", 3, 5], 5]     # 0.12465
["Round", ["BetaRegularized", 0.5, 2, 3], 4] # 0.6875
```

Without the extra installed, these constructs raise a clear
`ImportError` (naming the missing package) rather than failing with an
unrelated `ModuleNotFoundError` deep in the call stack.

### Deliberately excluded
`JacobiTheta`, `DedekindEta` - `scipy.special` doesn't implement these
either (no theta-function support), so the `special-functions` extra
above doesn't unlock them. A from-scratch q-series implementation would
carry the same "naive truncated series can be subtly wrong" risk noted
elsewhere in this section - a separate decision, not bundled in here.

---

## Combinatorics

```python
["Choose", 5, 2]                   # 10  (alias for the existing Binomial)
["Fibonacci", 10]                  # 55
["Multinomial", ["Array", 2, 3, 4]]  # 1260  (9! / (2!·3!·4!))
["Subfactorial", 4]                # 9   (derangements of 4 elements)
["BellNumber", 5]                  # 52  (ways to partition a 5-element set)
```

### PowerSet, Permutations, Combinations, CartesianProduct
Enumeration functions - each returns an array of arrays. **None of
these have a built-in output-size limit**: a set of `n` elements has
2ⁿ subsets, `n!` permutations, etc., so an innocuous-looking input
(`["PowerSet", ["Range", 30]]`) can already mean materializing over a
billion elements. If you're evaluating expressions from a source you
don't fully trust, disable these via `create_solver`'s `blacklist`
parameter (see the top-level README's "Restricting Available
Functions") rather than assuming they're safe against arbitrary input.

```python
["PowerSet", ["Array", 1, 2, 3]]
  # ["Array", ["Array"], ["Array",1], ["Array",2], ["Array",3],
  #   ["Array",1,2], ["Array",1,3], ["Array",2,3], ["Array",1,2,3]]

["Permutations", ["Array", 1, 2, 3]]        # all 3! = 6 orderings
["Permutations", ["Array", 1, 2, 3], 2]     # all 3·2 = 6 length-2 orderings
["Combinations", ["Array", 1, 2, 3], 2]     # ["Array", ["Array",1,2], ["Array",1,3], ["Array",2,3]]
["CartesianProduct", ["Array", 1, 2], ["Array", "a", "b"]]
  # ["Array", ["Array",1,"a"], ["Array",1,"b"], ["Array",2,"a"], ["Array",2,"b"]]
```

---

## Core

Structural introspection of the raw, unevaluated MathJSON tree - unlike
almost everything else on CortexJS's Core reference page (a
computer-algebra system, mutable state, LaTeX serialization - all out
of scope, see below), these don't need a type system or a rendering
surface.

### Head and Tail
The operator name and argument list of a compound expression -
inspected *without evaluating* the expression. `["Head", expr]` returns
`None` if `expr` isn't a compound (list) expression; `["Tail", expr]`
returns `["Array"]`.

```python
["Head", ["Add", 1, 2]]            # "Add"
["Tail", ["Add", 1, 2]]            # ["Array", 1, 2]
```

### Hold
Returns its argument completely unevaluated - the raw expression tree,
not its value.

```python
["Hold", ["Add", 1, 2]]            # ["Add", 1, 2]  (not 3.0)
```

### Identity
Returns its argument's evaluated value unchanged - unlike `Hold`, this
*does* evaluate it.

```python
["Identity", 42]                   # 42
["Identity", ["Add", 1, 2]]        # 3.0
```

### Type
The runtime kind of an expression's evaluated value: `"number"`,
`"string"`, `"boolean"`, `"array"`, `"nothing"` (for `None`), or a raw
Python type name for anything else.

```python
["Type", 5]                        # "number"
["Type", "hello"]                  # "string"
["Type", ["Array", 1, 2]]          # "array"
```

### IsSame and Same
Whether two expressions are structurally identical *as written* - same
shape, literals, and order - compared without evaluating either side.
Distinct from `Equal`/`StrictEqual` (which compare evaluated *values*)
and from the existing `IdenticallyEqual` (a stricter same-type
`StrictEqual`, also over evaluated values): this is a pre-evaluation,
syntactic check. CortexJS distinguishes `IsSame` from `Same` by
canonical-form normalization (e.g. treating `x+y` and `y+x` as
equivalent); this solver has no such normalization step, so both names
map to the same plain structural comparison here.

```python
["IsSame", ["Add", 1, 2], ["Add", 1, 2]]  # True
["IsSame", ["Add", 1, 2], ["Add", 2, 1]]  # False (different order, even though equal when evaluated)
```

### Deliberately excluded
- **CAS functions**: `Evaluate`, `Expand`, `ExpandAll`, `Factor`,
  `Together`, `Simplify`, `Solve`, `CanonicalForm`, `N`,
  `InverseFunction`, `Typed`, `DeclareType` - need a real
  computer-algebra system.
- **Mutable-state functions**: `Declare`, `Assign`, `Assume`,
  `HoldValues` - introduce statement sequencing and rebindable state
  into what's currently a pure expression tree.
- **LaTeX functions**: `Parse`, `Latex`, `LatexString`, `Subscript`,
  `Subminus`/`Subplus`/`Substar`,
  `Superdagger`/`Superminus`/`Superplus`/`Superstar` - presentation
  hints with no rendering surface in this solver.
- **`Error`/`IsError`** - CortexJS's in-tree error-tagging model. This
  solver already has a different, established error model
  (`MathJSONException`, raised as a Python exception) - not a gap, a
  different valid design already in place.
- **`Symbol`** - dynamically builds a symbol/identifier from
  concatenated string arguments. Low value given this solver already
  resolves bare-string parameter references directly.

---

## Comparison Operations

The _mathjson-solver_ provides two comparison operators that require additional explanation: `Equal` and `StrictEqual`, each designed to serve different use cases depending on the required level of strictness in comparisons.

The `Equal` operator is intentionally forgiving, allowing for more flexible comparisons where certain values are treated as equivalent even if they are of different types. For example, `Equal` considers `1` and `"1"` (a string representation of the number) as the same, making it useful in scenarios where type differences are not critical. Additionally, `Equal` treats `False`, `None`, and `0` as equivalent (all map to `"0"`), and `True` and `1` as equivalent (both map to `"1"`), consistent with Python's `bool`-as-`int` semantics.

On the other hand, `StrictEqual` enforces a more precise comparison by considering both the value and type. Under `StrictEqual`, `1` and `"1"` are distinct because one is an integer and the other is a string. Likewise, False and None are treated as separate entities, ensuring that comparisons strictly adhere to data type consistency. This makes `StrictEqual` ideal for cases where exact type matching is necessary to maintain data integrity.

### Equality

```python
["Equal", 1, "1"]                 # "1"=="1" = True
["StrictEqual", 1, "1"]           # "1"== 1 = False

["Equal", 10, 10]                 # 10==10 = True
["Equal", 10, 12]                 # 10==12 = False
["Equal", "aaa", "aaa"]           # "aaa" == "aaa" ➞ True
["Equal", "aaa", "bbb"]           # "aaa" == "bbb" ➞ False

# bool/int equivalence
["Equal", True, 1]                # True
["Equal", True, "1"]              # True
["Equal", False, 0]               # True
["Equal", False, None]            # True

["NotEqual", 1, 1]                # 1≠1 ➞  False
["NotEqual", 1, 2]                # 1≠2 ➞  True
["NotEqual", "aaa", "bbb"]        # "aaa≠"bbb" ➞  True
["NotEqual", "aaa", 0]            # "aaa≠0 ➞  True
```

### IdenticallyEqual
Stricter than `StrictEqual`: true only if both operands have the same Python type *and* are equal.

```python
["IdenticallyEqual", 1, 1]        # True
["IdenticallyEqual", 1, 1.0]      # False (int vs float)
["StrictEqual", 1, 1.0]           # True, for contrast
```

### IsTrue and IsFalse

Explicit truthiness checks. Prefer these over `Equal(x, 1)` when the intent is "did this condition hold?" — they mirror the truthiness semantics of `If`.

```python
["IsTrue", 1]                     # True
["IsTrue", 0]                     # False
["IsTrue", True]                  # True
["IsTrue", False]                 # False
["IsTrue", None]                  # False

["IsFalse", 0]                    # True
["IsFalse", 1]                    # False
["IsFalse", False]                # True
["IsFalse", True]                 # False
["IsFalse", None]                 # True
```

A typical use case is checking the result of `All` or `Any`:

```python
["If",
  [["IsTrue", ["All", ["Array", condition1, condition2]]], result],
  fallback
]
```

### Comparison

```python
["Greater", 1, 2]                 # 1>2 ➞ False
["Greater", 2, -2]                # 2>-2 ➞  True

["GreaterEqual", 1, 1]            # 1⩾1 ➞  True
["GreaterEqual", 2, 1]            # 2⩾1 ➞  True
["GreaterEqual", 1, 2]            # 1⩾2 ➞  False

["Less", 1, 1]                    # 1<1 ➞  False
["Less", 1, 2]                    # 1<2 ➞  True
["LessEqual", 1, 1]               # 1⩽1 ➞  True
["LessEqual", 1, 2]               # 1⩽2 ➞  True
```

### Congruent
Modular congruence: `a ≡ b (mod modulus)`.

```python
["Congruent", 7, 2, 5]            # True (7 - 2 = 5, divisible by 5)
["Congruent", 7, 3, 5]            # False
```

---

## Control Flow

### Constants
```
[
    "Constants",
    ["constant_name1", <expression>],
    ["constant_name2", <expression>],
    ["constant_name3", <expression>],
    ...,
    <expression>
]
```

`Constants` construct consists of keyword "Constants" followed by arbitrary number of name&value pairs. The last element in `Constants` construct is the expression to calculate using the defined constants.

The following example has two constants defined - `x=10` and `y=20`. Then the sum of these two constants is calculated and returned.

```python
[
    "Constants",
    ["x", 10],
    ["y", 20],
    ["Add","x", "y"]
]
```

#### Null propagation

If a constant definition raises an exception (e.g. because a referenced parameter is missing), that constant is set to `None` instead of crashing the entire expression. This allows `If` to select the valid branch at runtime:

```python
# With parameters = {"new_val": 22.5}   (old_val is missing)
[
    "Constants",
    ["c_old", ["Divide", "old_val", 2]],   # raises → None
    ["c_new", ["Divide", "new_val", 2]],   # 11.25
    ["If",
        [["Greater", "c_new", 0], "c_new"],
        "c_old"
    ]
]
# Result: 11.25  (c_old was never needed)
```

A constant that failed to compute resolves to `None`, which is falsy. Use `["IsFalse", "c_old"]` to detect it (or `["IsTrue", "c_old"]` to confirm it computed successfully).

### If Statement
```
[
    "If",
    [
        <true-or-false-expression>,
        <expression-to-calculate>
    ],
    [
        <elseif-true-or-false-expression>,
        <expression-to-calculate>
    ],
    ...,
    <else-expression-to-calculate>
]
```

Example:

```python
[
    "If",
    [
        ["Equal", 1, 0],
        10
    ],
    [
        ["Equal", 2, 2],
        20
    ],
    9000
]
```

This construct translates to:
```
if   1 == 0 then 10
elif 2 == 2 then 20
else 9000
```

`If` expressions do not need to be strictly _boolean_. Any value that is not _false_ are considered _true_.

#### CortexJS flat form

`If` also accepts the CortexJS flat form:

```
["If", <condition>, <then-expression>]
["If", <condition>, <then-expression>, <else-expression>]
```

```python
["If", ["Greater", "x", 3], 42, 99]   # 42 if x > 3, otherwise 99
["If", ["Greater", "x", 3], 42]       # 42 if x > 3, otherwise None (CortexJS "Nothing")
```

The two forms are detected automatically: in the pair form, `s[1]` is always a `[condition, value]` pair; in the flat form, `s[1]` *is* the condition. This is unambiguous as long as a pair-form condition that happens to be a bare parameter reference is wrapped in `IsTrue`/`IsFalse` (the pattern already recommended above) rather than used bare, e.g. prefer `[["IsTrue", "my_flag"], "yes"]` over `["my_flag", "yes"]`.

### Switch-Case Statement
```
["Switch", <on-expression>, <default-result-expression>, [<case1-expression>, <result-expression>], ...],
```

`Switch` construct consists of keyword "Switch" followed by expression whose value will be compared to _Cases'_ values. Then comes the default value. Then follows arbitrary number of _Cases_.

Example:

```python
["Switch", "color", 100, ["red", 10], ["blue", 20], ["green", 30]],
```

The expression in this example will make solver to look for a constant (or a parameter) with the name "color". If "color" is "red", expression evaluates to 10, if "blue" - to 20, if "green" - to 30. Otherwise to 100. Please note that "color" here is a valid expression that evaluates to the actual value of "color" whether it is a parameter or constant.

### Which
```
["Which", condition1, value1, condition2, value2, ..., conditionN, valueN]
```

`Which` is CortexJS's multi-branch conditional - **not** the same as `Switch`, despite both being "multi-branch". Each `condition` is a boolean expression (not a value to compare against), and `condition`/`value` are flat, separate arguments rather than nested `[case, result]` pairs. Evaluates each `condition` in order and returns the `value` paired with the first truthy one; later conditions and values are never evaluated. Returns `None` (CortexJS `Nothing`) if no condition matches.

```python
["Which", ["Equal", "x", 1], "a", ["Equal", "x", 2], "b"]   # "b", if x == 2
["Which", ["Equal", "x", 1], "a", ["Equal", "x", 2], "b"]   # None, if x is neither 1 nor 2
```

---

## Arrays and Aggregation

### Array

_MathJSON Solver_ supports static arrays and arrays given as parameters. Arrays can contain any number of elements, including other arrays. Arrays can be used in `Max`, `Min`, `Average`, `Median`, `Length`, `Any`, `All`, `In`, `ContainsAnyOf`, `ContainsAllOf`, `ContainsNoneOf`, `NotIn`.

A static array is defined as `["Array", 1, 2, 3]` and when evaluated, results to the same `["Array", 1, 2, 3]`.

An array can also be given as a parameter. In this case, the array is defined in the parameters dictionary and referred to by its name. For example, `parameters = {"a": ["Array", 1, 2, 3]}` and then the expression `["Max", "a"]` will result in 3.

Here is a full example with Sum:

```python
from mathjson_solver import create_solver

parameters = {"a": ["Array", 1, 1]}
expression = ["Sum", "a"]

solver = create_solver(parameters)
answer = solver(expression)

print(answer)
# 2, because ∑(1, 1)=2
```

### Statistical Functions

#### Average (alias: Mean)
`Average` internally tries to convert strings to numbers, making calculation of average from `[2, 4 ,"6"]` actually possible. Also, it ignores un-convertible elements so arrays like `[2, "three", 4 ,"6"]` don't crash the solver. `Mean` is the CortexJS name for the same function.

```python
["Average", ["Array", 1, 2, 3, 5, 2]]         # 2.6
["Average", ["Array", 2, "three", 4 ,"6"]]    # Average of [2, 4, 6] == 4,  element "three" is ignored
["Average", ["Array"]]                        # None
["Mean", ["Array", 2, 4, 6]]                  # 4
```

#### Max
Returns the maximum value from an array, or, in variadic (CortexJS) form, the maximum of the given arguments directly. Only considers numeric values and ignores non-numeric elements.

```python
["Max", ["Array", 1, 2, 3, 5, 2]] # 5
["Max", ["Array", 1, 2, ["Sum", 2, 4, 3], 5, 2]]  # 9
["Max", 5, 2, -1]                 # 5 (variadic form)
```

Max can also work with parameter references:

```python
# With parameters = {"a": ["Array", 1, 2, 3, 5, 2]}
["Max", "a"]                      # 5
```

#### Min
Returns the minimum value from an array, or, in variadic (CortexJS) form, the minimum of the given arguments directly. Only considers numeric values and ignores non-numeric elements.

```python
["Min", ["Array", 1, 2, 3, 5, 2]] # 1
["Min", ["Array", 2, 1, 3, 5, 2]] # 1
["Min", 5, 2, -1]                 # -1 (variadic form)
```

Min can also work with parameter references:

```python
# With parameters = {"a": ["Array", 2, 1, 3, 5, 2]}
["Min", "a"]                      # 1
```

#### Median
Returns the median value from an array. Only considers numeric values and ignores non-numeric elements.

```python
["Median", ["Array", 1, 2, 3, 5, 2]]  # 2
```

Median can also work with parameter references:

```python
# With parameters = {"a": ["Array", 1, 2, 3, 5, 2]}
["Median", "a"]                   # 2
```

#### Variance and StandardDeviation
Returns the (sample) variance and standard deviation of an array's numeric elements. `PopulationVariance`/`PopulationStandardDeviation` divide by `n` instead of `n-1`.

```python
["Round", ["Variance", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3]           # 4.571
["Round", ["StandardDeviation", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3]  # 2.138
["PopulationVariance", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]]               # 4
["PopulationStandardDeviation", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]]      # 2.0
```

#### Mode
Returns the most frequently occurring value. Ties go to whichever value appears first in the array.

```python
["Mode", ["Array", 1, 2, 2, 3]]                                        # 2
```

#### Quartiles and InterquartileRange
`Quartiles` returns the three points (Q1, Q2/median, Q3) that divide an array's numeric elements into four equal-sized groups. `InterquartileRange` is Q3 - Q1.

```python
["Quartiles", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]]                       # ["Array", 4.0, 4.5, 6.5]
["InterquartileRange", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]]              # 2.5
```

#### Covariance and Correlation
`Covariance` is the sample covariance of two equal-length arrays. `Correlation` is their Pearson correlation coefficient.

```python
["Covariance", ["Array", 1, 2, 3, 4, 5], ["Array", 2, 4, 6, 8, 10]]              # 5.0
["Round", ["Correlation", ["Array", 1, 2, 3, 4, 5], ["Array", 2, 4, 6, 8, 10]], 3]  # 1.0 (perfectly linear)
["Round", ["Correlation", ["Array", 1, 2, 3, 4, 5], ["Array", 5, 4, 3, 2, 1]], 3]   # -1.0 (perfectly anti-linear)
```

#### Skewness and Kurtosis
Sample-adjusted estimators - `Skewness` matches Excel's `SKEW` and `scipy.stats.skew(..., bias=False)`; `Kurtosis` is *excess* kurtosis (0 for a normal distribution), matching Excel's `KURT` and `scipy.stats.kurtosis(..., bias=False, fisher=True)`. `Skewness` needs at least 3 data points, `Kurtosis` at least 4.

```python
["Round", ["Skewness", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3]     # 0.818
["Round", ["Kurtosis", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3]     # 0.941
```

#### LinearRegression and PolynomialFit
`LinearRegression` returns the least-squares linear fit as `["Array", slope, intercept]`. `PolynomialFit` returns the least-squares fit of a given `degree` (0-50) as `["Array", c0, c1, ..., cd]`, representing `c0 + c1*x + c2*x^2 + ... + cd*x^d` (**lowest degree first** - the opposite order from `numpy.polyfit`). `PolynomialFit` solves the normal equations via Gaussian elimination rather than depending on numpy, which is less numerically stable for high degrees or badly-scaled data than a QR-based solver would be - keep degrees modest.

```python
["LinearRegression", ["Array", 1, 2, 3, 4, 5], ["Array", 3, 5, 7, 9, 11]]        # ["Array", 2.0, 1.0] (y = 2x + 1)
["PolynomialFit", ["Array", 0, 1, 2, 3, 4], ["Array", 3, 6, 11, 18, 27], 2]      # ≈ ["Array", 3.0, 2.0, 1.0] (y = x² + 2x + 3)
```

#### Probability Distributions
`NormalDistribution(mean, standardDeviation)`, `BinomialDistribution(n, p)`, `PoissonDistribution(lambda)`, `UniformDistribution(a, b)`, `ExponentialDistribution(lambda)` are "markers" - like `Function`, they return their own unevaluated expression rather than a computed value. `PDF`, `CDF`, and `Quantile` take one of these (inline, or via a solver parameter that holds one) as their first argument and do the actual computation, matching CortexJS's calling convention exactly.

```python
["PDF", ["BinomialDistribution", 4, ["Rational", 1, 2]], 2]   # 0.375
["Round", ["CDF", ["NormalDistribution", 0, 1], 1], 5]        # 0.84134  (Φ(1))
["Quantile", ["PoissonDistribution", 9], 0.95]                # 14

# A distribution can also be a solver parameter, not just inline:
solver = create_solver({"risk_model": ["NormalDistribution", 0, 1]})
solver(["CDF", "risk_model", 1.5])
```

No optional dependency is needed for `PDF` on any of the five distributions, or for `CDF`/`Quantile` on `NormalDistribution`/`UniformDistribution`/`ExponentialDistribution`. Only `CDF`/`Quantile` on `BinomialDistribution`/`PoissonDistribution` require the `special-functions` extra (`pip install mathjson-solver[special-functions]`) - they're built on the already-shipped `GammaRegularized`/`BetaRegularized` (via the identities `P(X≤k) = Q(k+1,λ)` for Poisson and `P(X≤k) = I_{1-p}(n-k,k+1)` for Binomial), which is both far more numerically robust and much faster than direct summation for large `n`/`λ` - the direct formula (`math.comb(n,k) * p**k * (1-p)**(n-k)`) actually overflows a float at `n` as low as 10,000, well within a realistic input range, since `math.comb` alone produces an enormous intermediate integer there. `PDF` on these two avoids that same overflow via a log-space reformulation instead (no scipy needed).

#### Length (alias: Count)
Returns the number of elements in an array, including non-numeric elements like `None`. `Count` is the CortexJS name for the same function.

```python
["Length", ["Array", 1, 2, 3, 5, 2, 9]]           # 6
["Length", ["Array"]]                             # 0
["Length", ["Array", 1, 2, 3, None]]              # 4
["Count", ["Array", 1, 2, 3]]                     # 3
```

Length can also work with parameter references:

```python
# With parameters = {"a": ["Array", 1, 2, 3, 5, 2, 9]}
["Length", "a"]                   # 6
```

### Array Manipulation Functions

#### List
CortexJS name for creating an array; behaves the same as `Array`.

```python
["List", 1, 2, 3]                                 # ["Array", 1, 2, 3]
```

#### First, Second, Third, Last, Rest, Most
Access or trim the ends of an array. `Second`/`Third` are fixed-position shortcuts, equivalent to `["At", array, 2]`/`["At", array, 3]`.

```python
["First", ["Array", 1, 2, 3]]                     # 1
["Second", ["Array", 1, 2, 3]]                     # 2
["Third", ["Array", 1, 2, 3]]                      # 3
["Last", ["Array", 1, 2, 3]]                       # 3
["Rest", ["Array", 1, 2, 3]]                       # ["Array", 2, 3] (all but the first)
["Most", ["Array", 1, 2, 3]]                       # ["Array", 1, 2] (all but the last)
```

#### Reverse and Sort

```python
["Reverse", ["Array", 1, 2, 3]]                    # ["Array", 3, 2, 1]
["Sort", ["Array", 3, 1, 2]]                        # ["Array", 1, 2, 3]
```

#### IsEmpty

```python
["IsEmpty", ["Array"]]                             # True
["IsEmpty", ["Array", 1]]                          # False
```

#### Unique and Dedup
`Unique` removes every duplicate, preserving the order of first occurrence. `Dedup` only removes *consecutive* duplicates.

```python
["Unique", ["Array", 1, 2, 2, 3, 1]]               # ["Array", 1, 2, 3]
["Dedup", ["Array", 1, 1, 2, 2, 2, 1, 3, 3]]       # ["Array", 1, 2, 1, 3]
```

#### Join
Concatenates two or more arrays.

```python
["Join", ["Array", 1, 2], ["Array", 3, 4]]         # ["Array", 1, 2, 3, 4]
```

#### Zip
Pairs up elements from two or more arrays by position.

```python
["Zip", ["Array", 1, 2], ["Array", "a", "b"]]      # ["Array", ["Array", 1, "a"], ["Array", 2, "b"]]
```

#### At
1-indexed element access (CortexJS convention), with negative indexes counting from the end. Compare to `AtIndex`, which is 0-indexed.

```python
["At", ["Array", 10, 20, 30], 1]                   # 10
["At", ["Array", 10, 20, 30], -1]                  # 30
```

#### Range
CortexJS-compatible range generator: 1 to `upper` inclusive by default, or `lower` to `upper` inclusive with an optional `step`. Compare to `GenerateRange`, which is 0-indexed and exclusive at the upper end.

```python
["Range", 5]                                       # ["Array", 1, 2, 3, 4, 5]
["Range", 2, 5]                                     # ["Array", 2, 3, 4, 5]
["Range", 1, 10, 2]                                 # ["Array", 1, 3, 5, 7, 9]
```

#### GenerateRange
Generates an array of sequential numbers starting from 0 or a specified start value.

```python
["GenerateRange", 3]                              # ["Array", 0, 1, 2]
["GenerateRange", 0]                              # ["Array"]
["GenerateRange", 0, 3, 1]                       # ["Array", 0, 1, 2]
["GenerateRange", 0, 10, 2]                      # ["Array", 0, 2, 4, 6, 8]
```

#### AtIndex
Returns the element at a specific index in an array (0-based indexing).

```python
["AtIndex", ["Array", 10, 20, 30, 40], 2]         # 30
```

#### Slice
Extracts a portion of an array between start and end indices (exclusive end).

```python
["Slice", ["Array", 10, 20, 30, 40, 50, 60], 2, 4]  # ["Array", 30, 40]
["Slice", ["Array", 10, 20, 30, 40, 50, 60], 2, 5]  # ["Array", 30, 40, 50]
```

#### Take and Drop
`Take`/`Drop` keep or remove the first `n` elements; a negative `n` counts from the end instead. Distinct from `Slice`, which takes an explicit `[start, end)` range rather than a count. `TakeWhile`/`DropWhile` take a predicate instead of a count - see [Predicate and function arguments](#predicate-and-function-arguments) below for the accepted forms.

```python
["Take", ["Array", 1, 2, 3, 4, 5], 3]              # ["Array", 1, 2, 3]
["Take", ["Array", 1, 2, 3, 4, 5], -2]              # ["Array", 4, 5]
["Drop", ["Array", 1, 2, 3, 4, 5], 2]               # ["Array", 3, 4, 5]
["TakeWhile", ["Array", 1, 2, 3, 10, 4], ["Function", ["Less", "_", 5]]]     # ["Array", 1, 2, 3]
["DropWhile", ["Array", 1, 2, 3, 10, 4], ["Function", ["Less", "_", 5]]]    # ["Array", 10, 4]
```

#### Contains, IndexOf, IndexWhere, Find, CountIf, Position
Searching and testing. `Contains` takes the collection first (`["Contains", array, value]`) - the opposite argument order from `In` (`["In", value, collection]`). `IndexOf`/`IndexWhere` are 1-indexed (CortexJS convention) and return `None` if nothing matches.

```python
["Contains", ["Array", 1, 2, 3], 2]                # True
["IndexOf", ["Array", "a", "b", "c"], "b"]         # 2
["IndexOf", ["Array", "a", "b", "c"], "z"]         # None
["IndexWhere", ["Array", 1, 2, 3, 4], ["Function", ["Greater", "_", 2]]]   # 3
["Find", ["Array", 1, 2, 3, 4], ["Function", ["Greater", "_", 2]]]        # 3 (the element, not its index)
["CountIf", ["Array", 1, 2, 3, 4, 5], ["Function", ["Greater", "_", 2]]]  # 3
["Position", ["Array", 1, 2, 3, 4, 5], ["Function", ["Greater", "_", 2]]] # ["Array", 3, 4, 5] (all matching indexes)
```

#### RotateLeft and RotateRight
Circularly shift an array by `n` positions.

```python
["RotateLeft", ["Array", 1, 2, 3, 4, 5], 2]        # ["Array", 3, 4, 5, 1, 2]
["RotateRight", ["Array", 1, 2, 3, 4, 5], 2]       # ["Array", 4, 5, 1, 2, 3]
```

#### MaxBy, MinBy, ArgMax, ArgMin, Ordering
`MaxBy`/`MinBy` return the element for which `function(element)` is largest/smallest. `ArgMax`/`ArgMin` return the 1-indexed position of the largest/smallest element directly (no function). `Ordering` returns the 1-indexed positions that would sort the array ascending.

```python
["MaxBy", ["Array", -5, 3, -2], ["Function", ["Abs", "_"]]]  # -5 (|-5| is largest)
["MinBy", ["Array", -5, 3, -2], ["Function", ["Abs", "_"]]]  # -2 (|-2| is smallest)
["ArgMax", ["Array", 3, 7, 2]]                     # 2 (position of 7)
["ArgMin", ["Array", 3, 7, 2]]                     # 3 (position of 2)
["Ordering", ["Array", 30, 10, 20]]                # ["Array", 2, 3, 1]
```

#### FlatMap, Scan, Differences, Fold
`FlatMap` applies `function` to each element (like `Map`) and splices any array results into a single flat array. `Scan` is like the CortexJS form of `Reduce`, but returns every intermediate accumulator value instead of just the final one. `Differences` gives successive differences. `Fold` is the function-first form of `Reduce`'s CortexJS calling convention (`["Fold", function, array]` instead of `["Reduce", array, function]`).

```python
["FlatMap", ["Array", 1, 2, 3], ["Function", ["Range", "_"]]]  # ["Array", 1, 1, 2, 1, 2, 3]
["Scan", ["Array", 1, 2, 3, 4], ["Add"]]           # ["Array", 1, 3.0, 6.0, 10.0]
["Differences", ["Array", 1, 3, 6, 10]]            # ["Array", 2, 3, 4]
["Fold", ["Add"], ["Array", 1, 2, 3, 4]]           # 10.0
```

#### Insert, DeleteAt, ReplaceAt, Append
Editing operations, 1-indexed like `At` (negative indexes count from the end). `Append` is CortexJS's name for the existing `Appended`.

```python
["Insert", ["Array", 1, 2, 4], 3, 3]               # ["Array", 1, 2, 3, 4]
["DeleteAt", ["Array", 1, 2, 3, 4], 2]              # ["Array", 1, 3, 4]
["ReplaceAt", ["Array", 1, 2, 3], 2, 99]            # ["Array", 1, 99, 3]
["Append", ["Array", 1, 2], 3]                      # ["Array", 1, 2, 3]
```

#### Partition, Chunk, GroupBy, ChunkBy, Tally
`Partition` splits into consecutive chunks of a fixed *size*; `Chunk` splits into a fixed *number* of roughly equal groups. `GroupBy` groups elements by a key function (returned as `[key, group]` pairs, in order of first appearance - there's no dedicated `Dictionary` type). `ChunkBy` only merges *consecutive* runs sharing a key. `Tally` counts occurrences of each distinct element.

```python
["Partition", ["Array", 1, 2, 3, 4, 5], 2]         # ["Array", ["Array", 1, 2], ["Array", 3, 4], ["Array", 5]]
["Chunk", ["Array", 1, 2, 3, 4, 5], 2]              # ["Array", ["Array", 1, 2, 3], ["Array", 4, 5]]
["GroupBy", ["Array", 1, 2, 3, 4, 5, 6], ["Function", ["Mod", "_", 2]]]
  # ["Array", ["Array", 1, ["Array", 1, 3, 5]], ["Array", 0, ["Array", 2, 4, 6]]]
["ChunkBy", ["Array", 1, 1, 2, 2, 1, 1], ["Function", "_"]]
  # ["Array", ["Array", 1, 1], ["Array", 2, 2], ["Array", 1, 1]]
["Tally", ["Array", "a", "b", "a", "c", "b", "a"]]
  # ["Array", ["Array", "a", 3], ["Array", "b", 2], ["Array", "c", 1]]
```

#### Predicate and function arguments
`TakeWhile`, `DropWhile`, `IndexWhere`, `Find`, `CountIf`, `Position`, `MaxBy`, `MinBy`, `FlatMap`, `GroupBy`, and `ChunkBy` all take a predicate or key function, using the same two forms as [`Map`](#map)/[`Filter`](#filter): a call template (e.g. `["IsPrime"]`, applied as `f(element)`) or a [`Function`](#function) expression (e.g. `["Function", ["Greater", "_", 2]]`).

#### Reduce
Reduces an array to a single value. Two calling conventions are supported, chosen automatically by argument count.

**CortexJS form** (3 or 4 arguments):
```python
["Reduce", array, function]
["Reduce", array, function, initial_value]
```
`function` is applied as `function(accumulator, current_item)` on each element; a call template (e.g. `["Add"]`) or a [`Function`](#function) expression can be used. Without `initial_value`, the first element seeds the accumulator.

```python
["Reduce", ["Array", 1, 2, 3, 4], ["Add"]]                                        # 10 (no initial value)
["Reduce", ["Array", 1, 2, 3, 4], ["Function", ["Add", "_1", "_2"]], 0]           # 10
["Reduce", ["Array", 1, 2, 3, 4], ["Function", ["Add", "acc", "n"], "acc", "n"], 0]  # 10
```

**Python form** (6 arguments): access to an accumulator, current element, *and* index — a powerful functional programming construct that enables stateful computations over arrays.

**Syntax:**
```python
["Reduce", array, initial_value, function_expression, accumulator_variable, current_variable, index_variable]
```

**Parameters:**
- `array`: The array to reduce
- `initial_value`: Starting value for the accumulator
- `function_expression`: Expression to apply on each iteration (uses direct variable names, not `["Variable", ...]`)
- `accumulator_variable`: Variable declaration for the accumulator (e.g., `["Variable", "acc"]`)
- `current_variable`: Variable declaration for the current element (e.g., `["Variable", "item"]`)
- `index_variable`: Variable declaration for the current index (e.g., `["Variable", "i"]`)

**Important:** In the `function_expression`, use direct variable names (e.g., `"accumulator"`, `"current_item"`), not variable declarations. Variable declarations (`["Variable", "name"]`) are only used in the parameter list.

**Simple Examples:**

```python
# Simple sum: equivalent to [1,2,3,4].reduce((acc, item) => acc + item, 0)
["Reduce", ["Array", 1, 2, 3, 4], 0,
  ["Add", "accumulator", "current_item"],
  ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]]  # 10

# Sum with index weighting: sum of (item * index)
["Reduce", ["Array", 5, 10, 15], 0,
  ["Add", "accumulator", ["Multiply", "current_item", "index"]],
  ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]]  # 40

# Building an array by appending elements
["Reduce", ["Array", 1, 2, 3, 4], ["Array"],
  ["Appended", "accumulator", "current_item"],
  ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]]  # ["Array", 1, 2, 3, 4]
```

**State Tuple Examples (Advanced):**

State tuples allow maintaining multiple accumulators simultaneously, essential for complex algorithms:

```python
# Accumulate both sum and count: [sum, count]
["Reduce", ["Array", 1, 2, 3, 4], ["Array", 0, 0],
  ["Appended",
    ["Appended",
      ["Array"],
      ["Add", ["AtIndex", "accumulator", 0], "current_item"]  # new_sum
    ],
    ["Add", ["AtIndex", "accumulator", 1], 1]                 # new_count
  ],
  ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]]
# Result: ["Array", 10, 4]

# Accumulate sum and product simultaneously: [sum, product]
["Reduce", ["Array", 2, 3, 4], ["Array", 0, 1],
  ["Appended",
    ["Appended",
      ["Array"],
      ["Add", ["AtIndex", "accumulator", 0], "current_item"]       # sum
    ],
    ["Multiply", ["AtIndex", "accumulator", 1], "current_item"]    # product
  ],
  ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]]
# Result: ["Array", 9, 24]

# Extract single value from state tuple using Constants and AtIndex
["Constants",
  ["state_result", [
    "Reduce", ["Array", 2, 3, 4], ["Array", 0, 1],
    ["Appended",
      ["Appended",
        ["Array"],
        ["Add", ["AtIndex", "accumulator", 0], "current_item"]
      ],
      ["Multiply", ["AtIndex", "accumulator", 1], "current_item"]
    ],
    ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]
  ]],
  ["AtIndex", "state_result", 0]  # Extract just the sum: 9
]
```

**Key Pattern for State Tuples:**
When building state tuples with multiple values, use the nested `Appended` pattern:
```python
["Appended",
  ["Appended",
    ["Array"],        # Start with empty array
    first_value       # Add first state value
  ],
  second_value        # Add second state value
]
```

This pattern can be extended for any number of state variables by adding more nested `Appended` calls.

#### Product
Multiplies together the numeric elements of an array.

```python
["Product", ["Array", 5, 7, 11]]                   # 385
```

#### Appended
Appends a value to the end of an array, returning a new array with the added element.

```python
["Appended", ["Array", 1, 2, 3], 4]                # ["Array", 1, 2, 3, 4]
["Appended", ["Array"], "first"]                   # ["Array", "first"]
```

#### CumulativeProduct
Calculates the cumulative product of array elements, returning an array where each element is the product of all elements up to that position.

```python
["CumulativeProduct", ["Array", 2, 3, 4, 5]]      # ["Array", 2, 6, 24, 120]
```

#### CumulativeSum
Calculates the cumulative sum of array elements, returning an array where each element is the sum of all elements up to that position.

```python
["CumulativeSum", ["Array", 1, 2, 3, 4, 5]]       # ["Array", 1, 3, 6, 10, 15]
```

---

## Boolean and Set Operations

### Boolean Operations

#### Boolean Literals
CortexJS represents booleans as the bare symbols `"True"`/`"False"`, distinct from native JSON `true`/`false` (which already evaluate correctly, since Python's `bool` is a `numbers.Number` subtype). Both forms now evaluate to actual booleans.

```python
"True"                             # True
"False"                            # False
["Equal", "flag", "True"]          # True, if the "flag" parameter is True
["And", "True", "True"]            # True
```

They are reserved literals: a solver parameter or local variable named `"True"`/`"False"` cannot shadow them.

#### Any
Returns `True` if any element in the array is truthy, `False` if all elements are falsy.

```python
["Any", ["Array", 0, 0, False, 0, 0]]             # False
["Any", ["Array", 0, 1, False, 0, 0]]             # True
```

#### All
Returns `True` if all elements in the array are truthy, `False` if any element is falsy.

```python
["All", ["Array", 0, 1, False, 0, 0]]             # False
["All", ["Array", 0, 1, False, "", 0]]            # False
["All", ["Array", 2, 1, True, "zz", 2]]           # True
```

#### Not
Returns the logical negation of a value. Any truthy value becomes `False`, any falsy value becomes `True`.

```python
["Not", True]                     # False
["Not", 0]                        # True
["Not", ["In", 2, ["Array", 1, 2, 3]]]  # False
```

#### And
Returns `True` if all conditions are truthy, `False` otherwise. Supports multiple conditions.

```python
["And", True, True]               # True
["And", True, False]              # False
["And", 1, 2, 3]                  # True (all truthy)
["And", 1, 0, 3]                  # False (0 is falsy)
["And", ["Greater", 5, 3], ["Less", 2, 4]]  # True
```

#### Or
Returns `True` if any condition is truthy, `False` if all are falsy. Supports multiple conditions.

```python
["Or", True, False]               # True
["Or", False, False]              # False
["Or", 0, 0, 1]                   # True (at least one truthy)
["Or", 0, "", False]              # False (all falsy)
["Or", ["Greater", 5, 3], ["Greater", 2, 4]]  # True
```

#### Xor, Nand, Nor, Implies, Equivalent
Two-argument (`Xor`, `Implies`, `Equivalent`) and variadic (`Nand`, `Nor`) logical connectives.

```python
["Xor", True, False]              # True (exclusive or)
["Xor", True, True]               # False
["Nand", True, True]              # False (not all truthy)
["Nand", True, False]             # True
["Nor", False, False]             # True (not any truthy)
["Nor", True, False]              # False
["Implies", True, False]          # False (p → q ≡ ¬p ∨ q)
["Implies", False, False]         # True
["Equivalent", True, True]        # True (p ↔ q)
["Equivalent", True, False]       # False
```

### Set Operations

#### In
Checks if a value is present in an array. Works with both static arrays and parameter references.

```python
["In", 2, ["Array", 1, 2, 3]]                     # True
["In", 4, ["Array", 1, 2, 3]]                     # False
["In", "Abc", ["Array", 1, 2, "Abc", 4]]          # True
["In", "Abc", ["Array", 1, 2, "Abcd", 4]]         # False
```

`In` also works with expressions and parameter references:

```python
["In", ["Add", 2, 2], ["Array", 1, 4, 3]]         # True
["In", ["Add", 2, 1], ["Array", 1, 2, ["Add", 1, 2]]]  # True

# With parameters = {"a": [10, 20, 30]}
["In", 20, "a"]                                   # True
["In", 21, "a"]                                   # False
```

#### Not_in / NotIn
Returns the opposite of `In` - `True` if the value is NOT in the array, `False` if it is present. Both `Not_in` and `NotIn` are aliases for the same function.

```python
["Not_in", 2, ["Array", 1, 2, 3]]                 # False
["Not_in", 4, ["Array", 1, 2, 3]]                 # True
["NotIn", 4, ["Array", 1, 2, 3]]                  # True

# With parameters = {"a": [10, 20, 30]}
["Not_in", 20, "a"]                               # False
["Not_in", 21, "a"]                               # True
```

#### Contains_any_of / ContainsAnyOf
Checks if the first array contains any elements from the second array. Both function names are aliases.

```python
["Contains_any_of", ["Array", 1, 2, 3], ["Array", 1, 2, 3]]        # True
["Contains_any_of", ["Array", 2, 3], ["Array", 1, 2]]              # True
["Contains_any_of", ["Array", 1, 2, 3], ["Array", 3, 4, 5, 6]]     # True
["Contains_any_of", ["Array", 1, 2, 3], ["Array", 4, 5, 6]]        # False
["ContainsAnyOf", ["Array", 1, 2, 3], ["Array", 4, 5, 6]]          # False
```

Works with expressions and parameter references:

```python
["Contains_any_of", ["Array", 1, ["Add", 1, 1], 6], ["Array", 4, 5, ["Add", 3, 3]]]  # True
["Contains_any_of", ["Array", 1, ["Add", 1, 1], 3], ["Array", 4, 5, ["Add", 3, 3]]]  # False

# With parameters = {"a": [10, 20, 30], "b": [1, 20, 3]}
["Contains_any_of", "a", "b"]                     # True
```

#### Contains_all_of / ContainsAllOf
Checks if the first array contains all elements from the second array. Both function names are aliases.

```python
["Contains_all_of", ["Array", 1, 2, 3], ["Array", 1, 2, 3]]        # True
["Contains_all_of", ["Array", 1, 2], ["Array", 1, 2, 3]]           # False
["Contains_all_of", ["Array", 1, 2, 3], ["Array", 1, 2]]           # True
["Contains_all_of", ["Array", 1, 2, 3], ["Array", 2]]              # True
["ContainsAllOf", ["Array", 1, 2, 3], ["Array", 2]]                # True
```

Works with parameter references:

```python
# With parameters = {"a": [1, 2, 3], "b": [1, 2]}
["Contains_all_of", "a", "b"]                     # True
```

#### Contains_none_of / ContainsNoneOf
Checks if the first array contains none of the elements from the second array. Both function names are aliases.

```python
["Contains_none_of", ["Array", 1, 2, 3], ["Array", 1, 2, 3]]       # False
["Contains_none_of", ["Array", 1, 2], ["Array", 2, 3]]             # False
["ContainsNoneOf", ["Array", 1, 2], ["Array", 2, 3]]               # False
["Contains_none_of", ["Array", 1, 2, 3], ["Array", 4, 5]]          # True
```

### Set Algebra
Basic set operations over `Array`, treating arrays as sets - there is no dedicated `Set` type in this solver.

#### Union and Intersection
Variadic (2 or more arrays), deduplicated, order-preserving.

```python
["Union", ["Array", 1, 2, 3], ["Array", 2, 3, 4]]                  # ["Array", 1, 2, 3, 4]
["Union", ["Array", 1, 2], ["Array", 2, 3], ["Array", 3, 4]]       # ["Array", 1, 2, 3, 4]
["Intersection", ["Array", 1, 2, 3], ["Array", 2, 3, 4]]           # ["Array", 2, 3]
["Intersection", ["Array", 1, 2], ["Array", 3, 4]]                 # ["Array"]
```

#### SetMinus and SymmetricDifference
Binary. `SetMinus` keeps `array1`'s elements not in `array2`; `SymmetricDifference` keeps elements in exactly one of the two.

```python
["SetMinus", ["Array", 1, 2, 3], ["Array", 2]]                     # ["Array", 1, 3]
["SymmetricDifference", ["Array", 1, 2, 3], ["Array", 2, 3, 4]]    # ["Array", 1, 4]
```

#### Element and NotElement
CortexJS's names for the existing `In`/`Not_in`, in the same argument order (`["Element", value, collection]`, matching mathematical `x ∈ S`).

```python
["Element", 2, ["Array", 1, 2, 3]]                                  # True
["NotElement", 9, ["Array", 1, 2, 3]]                               # True
```

---

## Type Conversion

### Int
Converts a value to an integer. Can handle string representations of numbers and floating-point numbers.

```python
["Int", "12"]                     # 12
["Int", "12.2"]                   # 12
```

### Float
Converts a value to a floating-point number.

```python
["Float", "12.2"]                 # 12.2
```

### Str
Converts a value to a string representation.

```python
["Str", 12]                       # "12"
["Str", "12"]                     # "12"
["Str", "aabb"]                   # "aabb"
```

### IsDefined
Returns `True` if the given name exists as a solver parameter or as a `Constants`-defined constant, `False` otherwise.

```python
# With parameters = {"a": 12}
["IsDefined", "a"]                # True
["IsDefined", "b"]                # False

# Inside Constants
["Constants", ["x", 5], ["IsDefined", "x"]]   # True
["Constants", ["x", 5], ["IsDefined", "y"]]   # False
```

### IsUndefined
The logical complement of `IsDefined`. Returns `True` if the name is not defined, `False` if it is.

```python
# With parameters = {"a": 12}
["IsUndefined", "a"]              # False
["IsUndefined", "b"]              # True

# Inside Constants
["Constants", ["x", 5], ["IsUndefined", "x"]]   # False
["Constants", ["x", 5], ["IsUndefined", "y"]]   # True
```

Note: when a `Constants` definition raises an exception, that constant is set to `None` (see null-propagation below). In that case `IsUndefined` still returns `False` — the name is defined, just with a `None` value. Use `["IsFalse", "val"]` to detect a failed constant (since `None` is falsy).

---

## Date and Time Functions

Date and time functions return **ISO format strings** by default, making them easy to use directly without additional formatting. When datetime arithmetic is needed, string dates are automatically parsed back to datetime objects.

### Current Date/Time

#### Today
Returns the current date as an ISO format string (`YYYY-MM-DD`).

```python
["Today"]                        # "2025-01-16"
["Strftime", ["Today"], "%Y"]    # "2025"
```

#### Now
Returns the current date and time as an ISO format string (`YYYY-MM-DDTHH:MM:SS.ffffff`).

```python
["Now"]                          # "2025-01-16T14:30:45.123456"
["Strftime", ["Now"], "%Y"]      # "2025"
```

### Date/Time Parsing and Formatting

#### Strptime
Parses a date/time string according to a format specification, returning an ISO format string.

```python
["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"]    # "2025-01-10T10:05:00"
["Strptime", "10/Jan/2025", "%d/%b/%Y"]               # "2025-01-10T00:00:00"
```

#### Strftime
Formats a datetime as a string according to a format specification. Accepts both datetime objects and ISO format strings as input.

```python
["Strftime", ["Today"], "%Y-%m-%d"]                   # "2025-01-16"
["Strftime", ["Now"], "%H:%M:%S"]                     # "14:30:45"
["Strftime", "2025-06-15T14:30:00", "%Y-%m-%d"]       # "2025-06-15" (string input)
["Strftime", "2025-06-15", "%B %d, %Y"]               # "June 15, 2025" (date string input)
```

### Time Deltas

Time delta functions create durations that can be added to or subtracted from dates. When used with `Add` or `Subtract`, string dates are automatically parsed and the result is returned as an ISO format string.

#### TimeDeltaDays
Creates a time delta representing a number of days.

```python
["Add", ["Today"], ["TimeDeltaDays", 7]]              # "2025-01-23T00:00:00"
["Subtract", ["Today"], ["TimeDeltaDays", 3]]         # "2025-01-13T00:00:00"
["Add", "2025-01-10", ["TimeDeltaDays", 5]]           # "2025-01-15T00:00:00" (string input)
```

#### TimeDeltaWeeks
Creates a time delta representing a number of weeks.

```python
["Add", ["Today"], ["TimeDeltaWeeks", 2]]             # "2025-01-30T00:00:00"
["Add", "2025-01-10", ["TimeDeltaWeeks", 1]]          # "2025-01-17T00:00:00"
```

#### TimeDeltaHours
Creates a time delta representing a number of hours.

```python
["Add", ["Now"], ["TimeDeltaHours", 3]]               # adds 3 hours to current time
["Add", "2025-01-10T10:00:00", ["TimeDeltaHours", 2]] # "2025-01-10T12:00:00"
```

#### TimeDeltaMinutes
Creates a time delta representing a number of minutes.

```python
["Add", ["Now"], ["TimeDeltaMinutes", 30]]            # adds 30 minutes to current time
["Add", "2025-01-10T10:00:00", ["TimeDeltaMinutes", 45]] # "2025-01-10T10:45:00"
```

### Combining Date Operations

Date functions can be chained together for complex date calculations:

```python
# Get the date 10 days from today, formatted
["Strftime", ["Add", ["Today"], ["TimeDeltaDays", 10]], "%B %d, %Y"]    # "January 26, 2025"

# Parse a date, add time, and format
["Strftime",
  ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaHours", 2]],
  "%H:%M"]                                                               # "12:05"

# Multiple time delta operations
["Add", ["Add", ["Today"], ["TimeDeltaDays", 1]], ["TimeDeltaHours", 12]]  # tomorrow at noon
```

---

## Trigonometric Functions

### Basic Trigonometric Functions

#### Sin
Computes the sine of an angle (in radians).

```python
["Sin", 0]                        # 0.0
["Sin", ["Pi"]]                   # ≈ 0.0 (actually very close to 0)
```

#### Cos
Computes the cosine of an angle (in radians).

```python
["Cos", 0]                        # 1.0
["Cos", ["Pi"]]                   # -1.0
```

#### Tan
Computes the tangent of an angle (in radians).

```python
["Tan", 0]                        # 0.0
```

### Inverse Trigonometric Functions

#### Arcsin
Computes the arcsine (inverse sine) of a value, returning result in radians.

```python
["Arcsin", 0]                     # 0.0
["Arcsin", 1]                     # π/2 ≈ 1.5708
```

#### Arccos
Computes the arccosine (inverse cosine) of a value, returning result in radians.

```python
["Arccos", 1]                     # 0.0
["Arccos", 0]                     # π/2 ≈ 1.5708
```

#### Arctan
Computes the arctangent (inverse tangent) of a value, returning result in radians.

```python
["Arctan", 0]                     # 0.0
["Arctan", 1]                     # π/4 ≈ 0.7854
```

#### Arctan2
Two-argument arctangent, `atan2(y, x)`, which correctly determines the quadrant of the result.

```python
["Arctan2", 1, 1]                 # π/4 ≈ 0.7854
["Arctan2", 1, -1]                # 3π/4 ≈ 2.3562
```

### Reciprocal Trigonometric Functions

```python
["Cot", ["Divide", ["Pi"], 4]]    # cot(π/4) ≈ 1.0
["Sec", 0]                        # sec(0) = 1.0
["Csc", ["Divide", ["Pi"], 2]]    # csc(π/2) = 1.0
["Arccot", 1]                     # π/4 ≈ 0.7854
["Arcsec", 1]                     # 0.0
["Arccsc", 1]                     # π/2 ≈ 1.5708
```

### Hyperbolic Functions

```python
["Sinh", 0]                       # 0.0
["Cosh", 0]                       # 1.0
["Tanh", 0]                       # 0.0
["Coth", 1]                       # coth(1) ≈ 1.3130
["Sech", 0]                       # 1.0
["Csch", 1]                       # csch(1) ≈ 0.8509
["Arsinh", 0]                     # 0.0
["Arcosh", 1]                     # 0.0
["Artanh", 0]                     # 0.0
["Arcoth", 2]                     # arcoth(2) ≈ 0.5493
["Arsech", 1]                     # 0.0
["Arcsch", 1]                     # arcsch(1) ≈ 0.8814
```

### Other

```python
["Hypot", 3, 4]                   # 5.0 (Euclidean distance / hypotenuse)
["Sinc", 0]                       # 1.0 (sin(x)/x, defined as 1 at x=0)
```

---

## Advanced Functions

### Map
Applies a function to each element of an array, returning a new array with the results. If the function fails for an element, the original element is preserved. `StrictMap` behaves the same but does not catch per-element failures.

The `function` argument accepts two forms: the original "call template" (a construct name wrapped in a list, e.g. `["Square"]`, with any trailing arguments to `Map` appended on every call), or a CortexJS-style [`Function`](#function) expression.

```python
["Map", ["Array", 1, 2, 3], ["Square"]]                    # ["Array", 1, 4, 9]
["Map", ["Array", 1, 2, 3, None, "a"], ["Square"]]         # ["Array", 1, 4, 9, None, "a"]
["Map", ["Array", 1, 2, 3], ["Power"], 2]                  # ["Array", 1, 4, 9]
["Map", ["Array", 1, 2, 3], ["GreaterEqual"], 2]           # ["Array", False, True, True]

# CortexJS Function form, anonymous placeholder
["Map", ["Array", 1, 2, 3, 4], ["Function", ["Multiply", "_", 2]]]      # ["Array", 2, 4, 6, 8]
# CortexJS Function form, named parameter
["Map", ["Array", 1, 2, 3], ["Function", ["Add", "n", 1], "n"]]         # ["Array", 2, 3, 4]
```

Complex example with aggregation:

```python
["Sum", ["Map", ["Array", 1, 2, 3, 4, 1, 1, 0, 1], ["GreaterEqual"], 2]]  # 3
```

### Filter
Keeps only the elements of an array for which `function` evaluates truthy. Takes the same `function` argument forms as `Map` (call template or `Function` expression).

```python
["Filter", ["Array", 1, 2, 3], ["LessEqual"], 2]                            # ["Array", 1, 2]
["Filter", ["Array", 1, 2, 3, 4, 5], ["Function", ["Greater", "_", 2]]]     # ["Array", 3, 4, 5]
```

### HasMatchingSublist
Advanced function for checking if a sublist within an array matches specific conditions.

**Syntax:**
```python
["HasMatchingSublist", array, required_match_count, position, contiguous, function, ...function_parameters]
```

**Parameters:**
- `array`: The array to search in
- `required_match_count`: Number of elements that must match the condition
- `position`: Where to look (0 = start, -1 = end, other numbers = specific position)
- `contiguous`: `True` for consecutive matches, `False` for anywhere in the range
- `function`: The function to apply to each element
- `function_parameters`: Additional parameters for the function

```python
# Check if first 3 elements are >= 1
["HasMatchingSublist", ["Array", 1, 2, 3, 4, 5, 6], 3, 0, True, ["GreaterEqual"], 1]   # True

# Check if first 3 elements are >= 2
["HasMatchingSublist", ["Array", 1, 2, 3, 4, 5, 6], 3, 0, True, ["GreaterEqual"], 2]   # False

# Check if any 3 elements are >= 4
["HasMatchingSublist", ["Array", 1, 2, 3, 4, 5, 6], 3, 0, False, ["GreaterEqual"], 4]  # True

# Check if last 3 elements are >= 4
["HasMatchingSublist", ["Array", 1, 2, 3, 4, 5, 6], 3, -1, True, ["GreaterEqual"], 4]  # True
```

---

## String Functions

### String and StringJoin
`String` concatenates the default string representation of each argument directly. `StringJoin` joins the elements of a single array, with an optional separator. Distinct from `Str` (a single-argument stringifier) and from `Join` (which concatenates multiple *arrays*, not strings - CortexJS's own `Join` is polymorphic, but this solver keeps `Join` array-only and gives strings their own dedicated name).

```python
["String", "a", 1, "b"]                            # "a1b"
["StringJoin", ["Array", "a", "b", "c"]]           # "abc"
["StringJoin", ["Array", "a", "b", "c"], "-"]      # "a-b-c"
```

### Case and Whitespace
```python
["ToUpperCase", "hello"]                           # "HELLO"
["ToLowerCase", "HELLO"]                           # "hello"
["CaseFold", "STRASSE"]                            # "strasse" (for case-insensitive comparison)
["Trim", "  hi  "]                                 # "hi"
["TrimStart", "  hi  "]                            # "hi  "
["TrimEnd", "  hi  "]                              # "  hi"
```

### StringSplit, StringReplace, StringCompare
`StringSplit` splits on whitespace by default, or on a literal separator if given. `StringReplace` replaces every occurrence of a literal substring (not pattern-based - see [Pattern Matching](#pattern-matching) for that). `StringCompare` returns -1, 0, or 1 by code-point sequence.

```python
["StringSplit", "a b  c"]                          # ["Array", "a", "b", "c"]
["StringSplit", "a,b,c", ","]                      # ["Array", "a", "b", "c"]
["StringReplace", "foo bar foo", "foo", "baz"]     # "baz bar baz"
["StringCompare", "abc", "abd"]                    # -1
["StringCompare", "abc", "abc"]                    # 0
```

### StringRepeat, PadStart, PadEnd
Capped at 100,000 characters, since their length is otherwise a direct, user-controlled memory-exhaustion vector.

```python
["StringRepeat", "ab", 3]                          # "ababab"
["PadStart", "7", 3, "0"]                          # "007"
["PadEnd", "7", 3, "0"]                             # "700"
["PadStart", "hello", 3]                           # "hello" (already long enough, pad char defaults to " ")
```

### Characters and GraphemeClusters
Splits a string into a list of its characters. Approximated at the Unicode code-point level (Python `str` iteration) rather than true extended grapheme clusters, which would need a dependency this solver doesn't otherwise require - a multi-codepoint grapheme (e.g. an emoji with a modifier) is split into its constituent code points rather than kept whole. `GraphemeClusters` is a CortexJS synonym for the same function.

```python
["Characters", "abc"]                              # ["Array", "a", "b", "c"]
```

### Encoding: Utf8, Utf16, UnicodeScalars, StringFrom
Convert a string to a list of code units in a given encoding, and back. `StringFrom`'s `encoding` argument is one of `"utf-8"`, `"utf-16"`, `"unicode-scalars"`.

```python
["Utf8", "hi"]                                     # ["Array", 104, 105]
["Utf16", "hi"]                                    # ["Array", 104, 105]
["UnicodeScalars", "hi"]                           # ["Array", 104, 105]
["StringFrom", ["Array", 104, 105], "utf-8"]       # "hi"
```

### IntegerString, DigitsFrom, NumberFrom
Convert integers to/from a string representation in an arbitrary base (2-36, default 10). `NumberFrom` parses a general numeric literal (integer, decimal, or scientific notation).

```python
["IntegerString", 255, 16]                         # "ff"
["IntegerString", -255, 16]                        # "-ff"
["DigitsFrom", "ff", 16]                            # 255
["NumberFrom", "3.14e2"]                            # 314.0
```

---

## Pattern Matching

`RegExp`, `IsMatch`, `StringMatch`, and `StringMatchAll` require the optional `regex` extra:

```bash
pip install mathjson-solver[regex]
```

This installs [RE2](https://github.com/google/re2), used instead of Python's `re`. RE2 matches via automaton simulation instead of backtracking, so it's mathematically incapable of catastrophic backtracking (ReDoS) - a real risk for a solver that evaluates untrusted expressions with no execution budget of its own, since a single crafted pattern can hang a backtracking engine indefinitely regardless of input size. The trade-off: **no backreferences or lookahead/lookbehind** (inherently backtracking-only features no linear-time engine can offer). Everything else you'd expect works: character classes, quantifiers, alternation, anchors, capturing groups (including named groups), and inline flags.

If the `regex` extra isn't installed, calling any of these functions raises a clear `ImportError` explaining how to install it.

### RegExp
Compiles a pattern (optional `i`/`m`/`s` flags: case-insensitive, multiline anchors, dot-matches-newline) into a reusable value, for passing to `IsMatch`/`StringMatch`/`StringMatchAll`. A bare pattern string works too, everywhere a pattern is expected - `RegExp` is only needed for flags or to reuse a compiled pattern.

```python
["RegExp", "hello", "i"]                           # a reusable case-insensitive pattern value
```

### IsMatch
Whether a string contains a match for a pattern (a bare string, or a `RegExp` value) anywhere within it.

```python
["IsMatch", "hello world", "wor.d"]                # True
["IsMatch", "HELLO", ["RegExp", "hello", "i"]]     # True
["IsMatch", "HELLO", "hello"]                      # False (case-sensitive without the "i" flag)
```

### StringMatch and StringMatchAll
`StringMatch` returns the first match; `StringMatchAll` returns every non-overlapping match. Each match is `["Array", matched_text, start, end, ["Array", group, ...]]` (1-indexed `start`, exclusive `end`, matching this solver's other CortexJS-index conventions). `StringMatch` returns `None` if there's no match.

```python
["StringMatch", "contact: alice@example", r"(\w+)@(\w+)"]
  # ["Array", "alice@example", 10, 22, ["Array", "alice", "example"]]

["StringMatchAll", "a1 b22 c333", r"\d+"]
  # ["Array",
  #   ["Array", "1", 2, 2, ["Array"]],
  #   ["Array", "22", 5, 6, ["Array"]],
  #   ["Array", "333", 9, 11, ["Array"]]]
```

---

## Integration Functions

### Variable
References a variable in expressions. The usage of `Variable` depends on the context:

**Integration Context:**
Used with `TrapezoidalIntegrate` to define the integration variable.

```python
["Variable", "x"]  # References variable "x" for integration
```

**Reduce Context (Variable Declarations):**
Used only in the parameter list of `Reduce` to declare variable names. In the function expression itself, use direct variable names.

```python
# Correct usage in Reduce
["Reduce", ["Array", 1, 2, 3], 0,
  ["Add", "accumulator", "current_item"],        # Direct variable names in expression
  ["Variable", "accumulator"],                   # Variable declaration
  ["Variable", "current_item"],                  # Variable declaration
  ["Variable", "index"]                          # Variable declaration
]

# INCORRECT - Don't use ["Variable", ...] inside the function expression:
["Reduce", ["Array", 1, 2, 3], 0,
  ["Add", ["Variable", "accumulator"], ["Variable", "current_item"]],  # Wrong!
  ["Variable", "accumulator"], ["Variable", "current_item"], ["Variable", "index"]
]
```

**General Rule:**
- Use `["Variable", "name"]` for variable **declarations** (parameter lists, integration variables)
- Use `"name"` (direct string) for variable **references** in expressions

### TrapezoidalIntegrate
Computes a numerical integral using the trapezoidal rule. **Requires numpy to be installed.**

**Syntax:**
```python
["TrapezoidalIntegrate", function_expression, start, end, n, variable]
```

**Parameters:**
- `function_expression`: The function to integrate
- `start`: Lower integration limit
- `end`: Upper integration limit
- `n`: Number of intervals for the trapezoidal rule
- `variable`: The integration variable (defined using `["Variable", "variable_name"]`)

**Examples:**

```python
# Polynomial Function f(x) = x²
["TrapezoidalIntegrate", ["Power", ["Variable", "x"], 2], 0, 1, 10, ["Variable", "x"]]  # ≈ 0.335

# Trigonometric Function f(x) = sin(x)
["TrapezoidalIntegrate", ["Sin", ["Variable", "x"]], 0, ["Pi"], 100, ["Variable", "x"]]  # ≈ 2.0

# Exponential Function f(x) = e^x
["TrapezoidalIntegrate", ["Exp", ["Variable", "x"]], 0, 1, 100, ["Variable", "x"]]  # ≈ 1.718
```

### Interp
Performs linear interpolation between data points. Given arrays of x and y values, interpolates the y value for a given x.

```python
["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 2.5]     # 25
["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 1]       # 10
["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 3]       # 30
["Interp", ["Array", 1, 3, 4], ["Array", 10, 30, 40], 2]       # 20
```

### FindIntervalIndex
Finds the interval index where a value falls within a sorted array of bounds. Returns the index of the interval that contains the value.

```python
# With age_bounds = [0, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
["FindIntervalIndex", ["Array", 0, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80], 42.5]  # 5
["FindIntervalIndex", ["Array", 0, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80], 20]    # 1
["FindIntervalIndex", ["Array", 0, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80], 80]    # 12
```

### Function
Defines a CortexJS-style lambda:

```
["Function", body_expression, param_name1, param_name2, ...]
```

`body_expression` is evaluated with the given parameter names bound to whatever arguments the function is called with. `Function` expressions are meant to be passed as the `function` argument of [`Map`](#map), [`Filter`](#filter), and [`Reduce`](#reduce), which call them with 1 argument (the element) or 2 (accumulator, current item) respectively.

If no parameter names are given, the anonymous placeholders `"_"` (bound only when there is a single argument) and `"_1"`, `"_2"`, ... (always bound, in order) are used instead:

```python
["Function", ["Multiply", "_", 2]]           # body refers to its single argument as "_"
["Function", ["Add", "_1", "_2"]]            # body refers to two arguments as "_1" and "_2"
["Function", ["Add", "acc", "n"], "acc", "n"]  # named parameters
```

Evaluating a `["Function", ...]` expression outside of such a context (i.e. not consumed by `Map`/`Filter`/`Reduce`) just returns it unevaluated.

**Note:** a parameter name bound inside a `Function` body correctly shadows a top-level solver parameter of the same name.

---

## Complex Examples

```python
# Complex expressions can be nested within each other
["Add", ["Multiply", 2, 3], ["Subtract", 10, 5]]  # (2*3) + (10-5) = 6 + 5 = 11
```

---

## Complete Function Reference

### Basic Operations
- [Add](#add) - Addition with type conversion
- [AddScalar](#addscalar) - Add scalar to each array element
- [AddArray](#addarray) - Element-wise array addition
- [Sum](#sum) - Sum with nested array support
- [Negate](#negate) - Sign inversion
- [Subtract](#subtract) - Subtraction
- [SubtractScalar](#subtractscalar) - Subtract scalar from each array element
- [SubtractArray](#subtractarray) - Element-wise array subtraction
- [Multiply](#multiply) - Multiplication
- [MultiplyByScalar](#multiplybyscalar) - Multiply each array element by scalar
- [MultiplyByArray](#multiplybyarray) - Element-wise array multiplication
- [Divide](#divide) - Division

### Mathematical Functions
- [Power](#power-and-square) - Exponentiation
- [Square](#power-and-square) - Square (x²)
- [Root](#root-and-square-root) - nth root
- [Sqrt](#root-and-square-root) - Square root
- [Exp](#exponents-and-logarithms) - Exponential (eˣ)
- [Log](#exponents-and-logarithms) - Base-10 logarithm, or base-`b` with a 2nd argument
- [Log2 / Lb](#exponents-and-logarithms) - Base-2 logarithm
- [Log10 / Lg](#exponents-and-logarithms) - Base-10 logarithm
- [Ln](#exponents-and-logarithms) - Natural logarithm
- [LogOnePlus](#exponents-and-logarithms) - ln(x + 1)
- [Abs](#absolute-value) - Absolute value
- [Round](#rounding) - Rounding
- [Floor](#floor-and-ceiling) - Floor function
- [Ceil](#floor-and-ceiling) - Ceiling function
- [Chop, Mod, Clamp](#number-theory-and-special-functions) - Zero snapping, Euclidean modulus, bounding
- [GCD, LCM](#number-theory-and-special-functions) - Greatest common divisor, least common multiple
- [Factorial, Binomial](#number-theory-and-special-functions) - Factorial, binomial coefficient
- [IsPrime](#number-theory-and-special-functions) - Primality test
- [Erf, Erfc](#number-theory-and-special-functions) - Error function and its complement
- [MachineEpsilon, CatalanConstant, EulerGamma](#constants) - More constants
- [Rational, Numerator, Denominator](#rational-numbers) - Rational number support (approximate)

### Number Theory
- [PowerMod, ModularInverse, IntegerSqrt](#powermod-modularinverse-integersqrt) - stdlib-based modular arithmetic
- [FactorInteger, PrimeFactors, PrimeNu, PrimeOmega, Radical, IsSquareFree](#factorinteger-primefactors-primenu-primeomega-radical-issquarefree) - Factorization
- [Divisors, Sigma0, Sigma1, SigmaMinus1, DivisorSigma](#divisors-sigma0-sigma1-sigmaminus1-divisorsigma) - Divisor functions
- [Divides, Totient](#divides-and-totient) - Divisibility and Euler's totient
- [IsPerfectPower](#isperfectpower) - a = b^k test
- [NthPrime, NextPrime, PrimePi](#nthprime-nextprime-primepi) - Prime lookups (capped)
- [ExtendedGCD, ChineseRemainder](#extendedgcd-and-chineseremainder) - Bézout coefficients, CRT
- [CarmichaelLambda, JacobiSymbol, LegendreSymbol, MultiplicativeOrder, PrimitiveRoot](#carmichaellambda-jacobisymbol-legendresymbol-multiplicativeorder-primitiveroot) - Modular structure
- [LucasL, CatalanNumber, BernoulliB](#lucasl-catalannumber-bernoullib) - Named number sequences
- [ContinuedFraction, FromContinuedFraction](#continuedfraction-and-fromcontinuedfraction) - Continued fractions
- [IntegerDigits, DigitCount, DigitSum, FromDigits](#integerdigits-digitcount-digitsum-fromdigits) - Digit manipulation (array form)
- [IsSquare, IsTriangular, IsPentagonal, IsOctahedral, IsCenteredSquare, IsPerfect, IsAbundant, IsHappy](#figurate-numbers-and-other-predicates) - Figurate numbers and other predicates

### Special Functions
- [Gamma, GammaLn, Beta, Factorial2](#gamma-gammaln-beta-factorial2) - Gamma-based functions
- [ErfInv, LambertW, AGM, EllipticK, EllipticE](#erfinv-lambertw-agm-elliptick-elliptice) - Verified iterative algorithms
- [Hypergeometric1F1, Hypergeometric2F1](#hypergeometric1f1-hypergeometric2f1) - Confluent and Gauss hypergeometric functions
- [BesselJ, BesselY, BesselI, BesselK, AiryAi, AiryBi, AiryAiPrime, AiryBiPrime, Zeta, GammaRegularized, BetaRegularized](#besselj-bessely-besseli-besselk-airyai-airybi-airyaiprime-airybiprime-zeta-gammaregularized-betaregularized) - Requires the optional `special-functions` extra (scipy)

### Combinatorics
- [Choose, Fibonacci, Multinomial, Subfactorial, BellNumber](#combinatorics) - Counting functions with no explosion risk
- [PowerSet, Permutations, Combinations, CartesianProduct](#powerset-permutations-combinations-cartesianproduct) - Enumeration functions (no output-size limit - see `blacklist` in the top-level README)

### Core
- [Head, Tail](#head-and-tail) - Operator name / argument list of a compound expression
- [Hold](#hold) - Return an argument unevaluated
- [Identity](#identity) - Return an argument's evaluated value unchanged
- [Type](#type) - Runtime kind of an evaluated value
- [IsSame, Same](#issame-and-same) - Structural (pre-evaluation) equality

### Comparison Operations
- [Equal](#equality) - Flexible equality (bool/int aware)
- [StrictEqual](#equality) - Strict equality
- [IdenticallyEqual](#identicallyequal) - Strict equality that also requires matching types
- [NotEqual](#equality) - Inequality
- [Greater](#comparison) - Greater than
- [GreaterEqual](#comparison) - Greater than or equal
- [Less](#comparison) - Less than
- [LessEqual](#comparison) - Less than or equal
- [Congruent](#congruent) - Modular congruence
- [IsTrue](#istrue-and-isfalse) - Explicit truthiness check
- [IsFalse](#istrue-and-isfalse) - Explicit falsiness check

### Control Flow
- [Constants](#constants-1) - Define constants
- [If](#if-statement) - Conditional statements (Python pair form and CortexJS flat form)
- [Switch](#switch-case-statement) - Value-equality switch-case statement
- [Which](#which) - CortexJS multi-branch conditional (flat condition/value chain, not the same as `Switch`)

### Arrays and Aggregation
- [Array / List](#array) - Array creation and manipulation
- [Average / Mean](#average-alias-mean) - Calculate average
- [Max](#max) - Maximum value (list or variadic)
- [Min](#min) - Minimum value (list or variadic)
- [Median](#median) - Median value
- [Mode](#mode) - Most frequently occurring value
- [Variance, StandardDeviation, PopulationVariance, PopulationStandardDeviation](#variance-and-standarddeviation) - Dispersion statistics
- [Quartiles, InterquartileRange](#quartiles-and-interquartilerange) - Quartile statistics
- [Covariance, Correlation](#covariance-and-correlation) - Two-array statistics
- [Skewness, Kurtosis](#skewness-and-kurtosis) - Distribution shape statistics
- [LinearRegression, PolynomialFit](#linearregression-and-polynomialfit) - Least-squares curve fitting
- [NormalDistribution, BinomialDistribution, PoissonDistribution, UniformDistribution, ExponentialDistribution, PDF, CDF, Quantile](#probability-distributions) - Probability distributions
- [Length / Count](#length-alias-count) - Array length
- [First, Second, Third, Last, Rest, Most](#first-second-third-last-rest-most) - Access or trim array ends
- [Reverse, Sort](#reverse-and-sort) - Reverse or sort an array
- [IsEmpty](#isempty) - Check if array is empty
- [Unique, Dedup](#unique-and-dedup) - Remove duplicates (all, or consecutive-only)
- [Join](#join) - Concatenate arrays
- [Zip](#zip) - Pair up elements from arrays
- [At](#at) - 1-indexed element access
- [Range](#range) - CortexJS-compatible range generator
- [GenerateRange](#generaterange) - Generate sequential number arrays (0-indexed)
- [AtIndex](#atindex) - Get element at specific index (0-indexed)
- [Slice](#slice) - Extract array portion
- [Take, Drop, TakeWhile, DropWhile](#take-and-drop) - Slice by count or predicate
- [Contains, IndexOf, IndexWhere, Find, CountIf, Position](#contains-indexof-indexwhere-find-countif-position) - Searching and testing
- [RotateLeft, RotateRight](#rotateleft-and-rotateright) - Circular shift
- [MaxBy, MinBy, ArgMax, ArgMin, Ordering](#maxby-minby-argmax-argmin-ordering) - Key-based extrema and sort order
- [FlatMap, Scan, Differences, Fold](#flatmap-scan-differences-fold) - Transformation
- [Insert, DeleteAt, ReplaceAt, Append](#insert-deleteat-replaceat-append) - Editing
- [Partition, Chunk, GroupBy, ChunkBy, Tally](#partition-chunk-groupby-chunkby-tally) - Grouping
- [CumulativeProduct](#cumulativeproduct) - Cumulative product calculation
- [CumulativeSum](#cumulativesum) - Cumulative sum calculation
- [Reduce](#reduce) - Reduce array to single value (CortexJS `fn` form or Python accumulator form)
- [Product](#product) - Multiply array elements together
- [Appended](#appended) - Append value to array

### Boolean and Set Operations
- [Boolean Literals (`True`/`False`)](#boolean-literals) - Bare boolean symbols
- [Any](#any) - Check if any element is truthy
- [All](#all) - Check if all elements are truthy
- [Not](#not) - Logical negation
- [And](#and) - Logical AND operation
- [Or](#or) - Logical OR operation
- [Xor, Nand, Nor, Implies, Equivalent](#xor-nand-nor-implies-equivalent) - Other logical connectives
- [In](#in) - Check membership
- [Not_in / NotIn](#not_in--notin) - Check non-membership
- [Contains_any_of / ContainsAnyOf](#contains_any_of--containsanyof) - Check overlap
- [Contains_all_of / ContainsAllOf](#contains_all_of--containsallof) - Check subset
- [Contains_none_of / ContainsNoneOf](#contains_none_of--containsnoneof) - Check disjoint
- [Union, Intersection](#union-and-intersection) - Combine or overlap two or more arrays
- [SetMinus, SymmetricDifference](#setminus-and-symmetricdifference) - Array difference operations
- [Element, NotElement](#element-and-notelement) - CortexJS names for `In`/`Not_in`

### Type Conversion
- [Int](#int) - Convert to integer
- [Float](#float) - Convert to float
- [Str](#str) - Convert to string
- [IsDefined](#isdefined) - Check if defined
- [IsUndefined](#isundefined) - Check if not defined

### Date and Time Functions
- [Today](#today) - Current date (ISO string)
- [Now](#now) - Current date/time (ISO string)
- [Strptime](#strptime) - Parse date/time string (returns ISO string)
- [Strftime](#strftime) - Format date/time (accepts strings)
- [TimeDeltaDays](#timedeltadays) - Day time delta
- [TimeDeltaWeeks](#timedeltaweeks) - Week time delta
- [TimeDeltaHours](#timedeltahours) - Hour time delta
- [TimeDeltaMinutes](#timedeltaminutes) - Minute time delta

### Trigonometric Functions
- [Sin](#sin) - Sine
- [Cos](#cos) - Cosine
- [Tan](#tan) - Tangent
- [Arcsin](#arcsin) - Arcsine
- [Arccos](#arccos) - Arccosine
- [Arctan](#arctan) - Arctangent
- [Arctan2](#arctan2) - Two-argument arctangent
- [Cot, Sec, Csc](#reciprocal-trigonometric-functions) - Reciprocal trig functions
- [Arccot, Arcsec, Arccsc](#reciprocal-trigonometric-functions) - Inverse reciprocal trig functions
- [Sinh, Cosh, Tanh, Coth, Sech, Csch](#hyperbolic-functions) - Hyperbolic functions
- [Arsinh, Arcosh, Artanh, Arcoth, Arsech, Arcsch](#hyperbolic-functions) - Area hyperbolic (inverse) functions
- [Hypot](#other) - Euclidean distance / hypotenuse
- [Sinc](#other) - Sinc function
- [Pi, Degrees, ExponentialE, GoldenRatio](#constants) - Constants

### Advanced Functions
- [Map / StrictMap](#map) - Apply function to array elements
- [Filter](#filter) - Keep array elements matching a condition
- [HasMatchingSublist](#hasmatchingsublist) - Advanced sublist matching

### String Functions
- [String, StringJoin](#string-and-stringjoin) - Concatenate values or join an array of strings
- [ToUpperCase, ToLowerCase, CaseFold](#case-and-whitespace) - Case conversion
- [Trim, TrimStart, TrimEnd](#case-and-whitespace) - Whitespace trimming
- [StringSplit, StringReplace, StringCompare](#stringsplit-stringreplace-stringcompare) - Splitting, literal replace, ordering
- [StringRepeat, PadStart, PadEnd](#stringrepeat-padstart-padend) - Repetition and padding (length-capped)
- [Characters / GraphemeClusters](#characters-and-graphemeclusters) - Split into characters
- [Utf8, Utf16, UnicodeScalars, StringFrom](#encoding-utf8-utf16-unicodescalars-stringfrom) - Encode/decode code units
- [IntegerString, DigitsFrom, NumberFrom](#integerstring-digitsfrom-numberfrom) - Base conversion and number parsing

### Pattern Matching
*(requires the optional `regex` extra: `pip install mathjson-solver[regex]`)*
- [RegExp](#regexp) - Compile a reusable pattern (RE2 syntax, optional flags)
- [IsMatch](#ismatch) - Test whether a string contains a match
- [StringMatch, StringMatchAll](#stringmatch-and-stringmatchall) - Find first or all matches, with capture groups

### Integration Functions
- [Function](#function) - CortexJS-style lambda, for use with Map/Filter/Reduce
- [Variable](#variable) - Variable reference
- [TrapezoidalIntegrate](#trapezoidalintegrate) - Numerical integration
- [Interp](#interp) - Linear interpolation
- [FindIntervalIndex](#findintervalindex) - Find interval index for value
