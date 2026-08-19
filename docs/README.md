# MathJSON Solver Documentation

## Table of Contents

1. [Basic Arithmetic](#basic-arithmetic)
2. [Mathematical Functions](#mathematical-functions)
3. [Comparison Operations](#comparison-operations)
4. [Control Flow](#control-flow)
5. [Arrays and Aggregation](#arrays-and-aggregation)
6. [Boolean and Set Operations](#boolean-and-set-operations)
7. [Type Conversion](#type-conversion)
8. [Date and Time Functions](#date-and-time-functions)
9. [Trigonometric Functions](#trigonometric-functions)
10. [Advanced Functions](#advanced-functions)
11. [Integration Functions](#integration-functions)

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
```

### Number Theory and Special Functions

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

`Which` is the CortexJS name for `Switch` and takes exactly the same arguments.

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
Returns the (sample) variance and standard deviation of an array's numeric elements.

```python
["Round", ["Variance", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3]           # 4.571
["Round", ["StandardDeviation", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3]  # 2.138
```

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

#### First, Last, Rest, Most
Access or trim the ends of an array.

```python
["First", ["Array", 1, 2, 3]]                     # 1
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

#### Unique
Removes duplicates, preserving the order of first occurrence.

```python
["Unique", ["Array", 1, 2, 2, 3, 1]]               # ["Array", 1, 2, 3]
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

#### Reduce
Reduces an array to a single value by iteratively applying a function that has access to an accumulator, current element, and index. This is a powerful functional programming construct that enables stateful computations over arrays.

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
Applies a function to each element of an array, returning a new array with the results. If the function fails for an element, the original element is preserved.

```python
["Map", ["Array", 1, 2, 3], ["Square"]]                    # ["Array", 1, 4, 9]
["Map", ["Array", 1, 2, 3, None, "a"], ["Square"]]         # ["Array", 1, 4, 9, None, "a"]
["Map", ["Array", 1, 2, 3], ["Power"], 2]                  # ["Array", 1, 4, 9]
["Map", ["Array", 1, 2, 3], ["GreaterEqual"], 2]           # ["Array", False, True, True]
```

Complex example with aggregation:

```python
["Sum", ["Map", ["Array", 1, 2, 3, 4, 1, 1, 0, 1], ["GreaterEqual"], 2]]  # 3
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
**Note: This is a placeholder function for future implementation.** Currently not functional.

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

### Comparison Operations
- [Equal](#equality) - Flexible equality (bool/int aware)
- [StrictEqual](#equality) - Strict equality
- [NotEqual](#equality) - Inequality
- [Greater](#comparison) - Greater than
- [GreaterEqual](#comparison) - Greater than or equal
- [Less](#comparison) - Less than
- [LessEqual](#comparison) - Less than or equal
- [IsTrue](#istrue-and-isfalse) - Explicit truthiness check
- [IsFalse](#istrue-and-isfalse) - Explicit falsiness check

### Control Flow
- [Constants](#constants) - Define constants
- [If](#if-statement) - Conditional statements
- [Switch / Which](#switch-case-statement) - Switch-case statements

### Arrays and Aggregation
- [Array / List](#array) - Array creation and manipulation
- [Average / Mean](#average-alias-mean) - Calculate average
- [Max](#max) - Maximum value (list or variadic)
- [Min](#min) - Minimum value (list or variadic)
- [Median](#median) - Median value
- [Variance, StandardDeviation](#variance-and-standarddeviation) - Dispersion statistics
- [Length / Count](#length-alias-count) - Array length
- [First, Last, Rest, Most](#first-last-rest-most) - Access or trim array ends
- [Reverse, Sort](#reverse-and-sort) - Reverse or sort an array
- [IsEmpty](#isempty) - Check if array is empty
- [Unique](#unique) - Remove duplicates
- [Join](#join) - Concatenate arrays
- [Zip](#zip) - Pair up elements from arrays
- [At](#at) - 1-indexed element access
- [Range](#range) - CortexJS-compatible range generator
- [GenerateRange](#generaterange) - Generate sequential number arrays (0-indexed)
- [AtIndex](#atindex) - Get element at specific index (0-indexed)
- [Slice](#slice) - Extract array portion
- [CumulativeProduct](#cumulativeproduct) - Cumulative product calculation
- [CumulativeSum](#cumulativesum) - Cumulative sum calculation
- [Reduce](#reduce) - Reduce array to single value with accumulator
- [Appended](#appended) - Append value to array

### Boolean and Set Operations
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
- [Map](#map) - Apply function to array elements
- [HasMatchingSublist](#hasmatchingsublist) - Advanced sublist matching

### Integration Functions
- [Function](#function) - Function definition (placeholder)
- [Variable](#variable) - Variable reference
- [TrapezoidalIntegrate](#trapezoidalintegrate) - Numerical integration
- [Interp](#interp) - Linear interpolation
- [FindIntervalIndex](#findintervalindex) - Find interval index for value
