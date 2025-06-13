# Numerical Integration Test Cases

## Basic Functions

1. **Polynomial Function**
   - Function: f(x) = x²
   - Limits: [0, 1]
   - Exact Result: 1/3
   - Formula: ∫₀¹ x² dx = [x³/3]₀¹ = 1/3

2. **Trigonometric Function**
   - Function: f(x) = sin(x)
   - Limits: [0, π]
   - Exact Result: 2
   - Formula: ∫₀ᵗ sin(x) dx = [-cos(x)]₀ᵗ = -cos(π) - (-cos(0)) = 1 - (-1) = 2

3. **Exponential Function**
   - Function: f(x) = e^x
   - Limits: [0, 1]
   - Exact Result: e - 1 ≈ 1.71828
   - Formula: ∫₀¹ e^x dx = [e^x]₀¹ = e¹ - e⁰ = e - 1

## Intermediate Functions

4. **Rational Function**
   - Function: f(x) = 1/(1+x²)
   - Limits: [0, 1]
   - Exact Result: π/4 ≈ 0.78540
   - Formula: ∫₀¹ 1/(1+x²) dx = [arctan(x)]₀¹ = arctan(1) - arctan(0) = π/4 - 0 = π/4

5. **Product of Functions**
   - Function: f(x) = x·sin(x)
   - Limits: [0, π]
   - Exact Result: π
   - Formula: ∫₀ᵗ x·sin(x) dx = [x·(-cos(x)) + sin(x)]₀ᵗ = π·(-cos(π)) + sin(π) - (0·(-cos(0)) + sin(0)) = π·1 + 0 - 0 = π

6. **Logarithmic Function**
   - Function: f(x) = ln(x)
   - Limits: [1, 2]
   - Exact Result: 2·ln(2) - 1 ≈ 0.38629
   - Formula: ∫₁² ln(x) dx = [x·ln(x) - x]₁² = 2·ln(2) - 2 - (1·ln(1) - 1) = 2·ln(2) - 2 - (-1) = 2·ln(2) - 1

## Advanced Functions

7. **Function with Singularity**
   - Function: f(x) = 1/√x
   - Limits: [0.01, 1]
   - Exact Result: 2·(1 - √0.01) ≈ 1.8
   - Formula: ∫₀.₀₁¹ 1/√x dx = [2√x]₀.₀₁¹ = 2·(1 - √0.01) = 2·(1 - 0.1) = 2·0.9 = 1.8

8. **Highly Oscillatory Function**
   - Function: f(x) = sin(10x)·cos(3x)
   - Limits: [0, 2π]
   - Exact Result: 0
   - Formula: Using trigonometric identities, this equals (1/2)(sin(13x) + sin(7x))
   - Integrated over a full period, the result is 0

9. **Function with Multiple Local Extrema**
   - Function: f(x) = x²·sin(1/x)
   - Limits: [0.1, 1]
   - No simple closed-form solution
   - Approximate Result: ≈ 0.287

## Challenging Cases for Numerical Methods

10. **Rapidly Varying Function**
    - Function: f(x) = e^(-x²)
    - Limits: [-5, 5]
    - Exact Result: √π ≈ 1.77245
    - Formula: ∫₋₅⁵ e^(-x²) dx ≈ ∫₋∞∞ e^(-x²) dx = √π

11. **Function with Discontinuity**
    - Function: f(x) = 1/x
    - Limits: [0.001, 1]
    - Exact Result: ln(1) - ln(0.001) = ln(1000) ≈ 6.90776
    - Formula: ∫₀.₀₀₁¹ 1/x dx = [ln|x|]₀.₀₀₁¹ = ln(1) - ln(0.001) = 0 - (-ln(1000)) = ln(1000)

12. **Function with Sharp Peak**
    - Function: f(x) = 1/(1+100x²)
    - Limits: [-1, 1]
    - Exact Result: (1/10)·arctan(10) - (1/10)·arctan(-10) = (1/10)·(arctan(10) + arctan(10)) = (2/10)·arctan(10) ≈ 0.29423
    - Formula: ∫₋₁¹ 1/(1+100x²) dx = (1/10)·[arctan(10x)]₋₁¹