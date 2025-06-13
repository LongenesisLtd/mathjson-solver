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

### Multiply
Performs basic multiplication.

```python
["Multiply", 2, 4]                # 2*4=8
["Multiply", 2, 3, 4]             # 2*3*4=24
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

```python
["Exp", 2]                        # e^2≅7.389
["Log", 2.7183]                   # ln(2.7183)≅1.0000
["Log2", 8]                       # log2(8)=3.0
["Log10", 1000]                   # log10(1000)=3.0
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

### Constants

```python
["Pi"]                            # 3.141592653589793
["Multiply", 2, ["Pi"]]           # 2π ≈ 6.283
```

---

## Comparison Operations

The _mathjson-solver_ provides two comparison operators that require additional explanation: `Equal` and `StrictEqual`, each designed to serve different use cases depending on the required level of strictness in comparisons.

The `Equal` operator is intentionally forgiving, allowing for more flexible comparisons where certain values are treated as equivalent even if they are of different types. For example, `Equal` considers `1` and `"1"` (a string representation of the number) as the same, making it useful in scenarios where type differences are not critical. Additionally, `Equal` treats `False` and `None` as equivalent, which can be beneficial in cases where both represent the absence or falsity of a value.

On the other hand, `StrictEqual` enforces a more precise comparison by considering both the value and type. Under `StrictEqual`, `1` and `"1"` are distinct because one is an integer and the other is a string. Likewise, False and None are treated as separate entities, ensuring that comparisons strictly adhere to data type consistency. This makes `StrictEqual` ideal for cases where exact type matching is necessary to maintain data integrity.

### Equality

```python
["Equal", 1, "1"]                 # "1"=="1" = True
["StrictEqual", 1, "1"]           # "1"== 1 = False

["Equal", 10, 10]                 # 10==10 = True
["Equal", 10, 12]                 # 10==12 = False
["Equal", "aaa", "aaa"]           # "aaa" == "aaa" ➞ True
["Equal", "aaa", "bbb"]           # "aaa" == "bbb" ➞ False

["NotEqual", 1, 1]                # 1≠1 ➞  False
["NotEqual", 1, 2]                # 1≠2 ➞  True
["NotEqual", "aaa", "bbb"]        # "aaa≠"bbb" ➞  True
["NotEqual", "aaa", 0]            # "aaa≠0 ➞  True
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

#### Average
`Average` internally tries to convert strings to numbers, making calculation of average from `[2, 4 ,"6"]` actually possible. Also, it ignores un-convertible elements so arrays like `[2, "three", 4 ,"6"]` don't crash the solver.

```python
["Average", ["Array", 1, 2, 3, 5, 2]]         # 2.6
["Average", ["Array", 2, "three", 4 ,"6"]]    # Average of [2, 4, 6] == 4,  element "three" is ignored
["Average", ["Array"]]                        # None
```

#### Max
Returns the maximum value from an array. Only considers numeric values and ignores non-numeric elements.

```python
["Max", ["Array", 1, 2, 3, 5, 2]] # 5
["Max", ["Array", 1, 2, ["Sum", 2, 4, 3], 5, 2]]  # 9
```

Max can also work with parameter references:

```python
# With parameters = {"a": ["Array", 1, 2, 3, 5, 2]}
["Max", "a"]                      # 5
```

#### Min
Returns the minimum value from an array. Only considers numeric values and ignores non-numeric elements.

```python
["Min", ["Array", 1, 2, 3, 5, 2]] # 1
["Min", ["Array", 2, 1, 3, 5, 2]] # 1
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

#### Length
Returns the number of elements in an array, including non-numeric elements like `None`.

```python
["Length", ["Array", 1, 2, 3, 5, 2, 9]]           # 6
["Length", ["Array"]]                             # 0
["Length", ["Array", 1, 2, 3, None]]              # 4
```

Length can also work with parameter references:

```python
# With parameters = {"a": ["Array", 1, 2, 3, 5, 2, 9]}
["Length", "a"]                   # 6
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
**Note: This is a placeholder function for future implementation.** Supposed to check if a parameter name exists in the parameters dictionary.

```python
# With parameters = {"a": 12}
["IsDefined", "b"]                # False
```

---

## Date and Time Functions

### Date/Time Parsing and Formatting

#### Strptime
Parses a date/time string according to a format specification, returning a datetime object.

```python
["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"]
```

#### Strftime
Formats a datetime object as a string according to a format specification.

```python
["Strftime", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], "%Y"]     # "2025"
["Strftime", ["Today"], "%Y"]                                              # "2025"
["Strftime", ["Now"], "%Y"]                                                # "2025"
```

### Current Date/Time

#### Today
Returns the current date (without time).

```python
["Strftime", ["Today"], "%Y"]    # "2025"
```

#### Now
Returns the current date and time.

```python
["Strftime", ["Now"], "%Y"]      # "2025"
```

### Time Deltas

#### TimeDeltaWeeks
Creates a time delta representing a number of weeks.

```python
["Strftime", ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaWeeks", 1]], "%d"]  # "17"
```

#### TimeDeltaHours
Creates a time delta representing a number of hours.

```python
["Strftime", ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaHours", 2]], "%H"]  # "12"
```

#### TimeDeltaMinutes
Creates a time delta representing a number of minutes.

```python
["Strftime", ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaMinutes", 5]], "%M"]  # "10"
```

#### TimeDeltaDays
Creates a time delta representing a number of days.

```python
["Strftime", ["Add", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaDays", 3]], "%d"]      # "13"
["Strftime", ["Subtract", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], ["TimeDeltaDays", 3]], "%d"] # "07"
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
References a variable in an integrable expression. Used specifically with `TrapezoidalIntegrate` to define the integration variable.

```python
["Variable", "x"]  # References variable "x"
```

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
- [Sum](#sum) - Sum with nested array support
- [Negate](#negate) - Sign inversion
- [Subtract](#subtract) - Subtraction
- [Multiply](#multiply) - Multiplication
- [Divide](#divide) - Division

### Mathematical Functions
- [Power](#power-and-square) - Exponentiation
- [Square](#power-and-square) - Square (x²)
- [Root](#root-and-square-root) - nth root
- [Sqrt](#root-and-square-root) - Square root
- [Exp](#exponents-and-logarithms) - Exponential (eˣ)
- [Log](#exponents-and-logarithms) - Natural logarithm
- [Log2](#exponents-and-logarithms) - Base-2 logarithm
- [Log10](#exponents-and-logarithms) - Base-10 logarithm
- [Abs](#absolute-value) - Absolute value
- [Round](#rounding) - Rounding

### Comparison Operations
- [Equal](#equality) - Flexible equality
- [StrictEqual](#equality) - Strict equality
- [NotEqual](#equality) - Inequality
- [Greater](#comparison) - Greater than
- [GreaterEqual](#comparison) - Greater than or equal
- [Less](#comparison) - Less than
- [LessEqual](#comparison) - Less than or equal

### Control Flow
- [Constants](#constants) - Define constants
- [If](#if-statement) - Conditional statements
- [Switch](#switch-case-statement) - Switch-case statements

### Arrays and Aggregation
- [Array](#array) - Array creation and manipulation
- [Average](#average) - Calculate average
- [Max](#max) - Maximum value
- [Min](#min) - Minimum value
- [Median](#median) - Median value
- [Length](#length) - Array length

### Boolean and Set Operations
- [Any](#any) - Check if any element is truthy
- [All](#all) - Check if all elements are truthy
- [Not](#not) - Logical negation
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

### Date and Time Functions
- [Strptime](#strptime) - Parse date/time string
- [Strftime](#strftime) - Format date/time
- [Today](#today) - Current date
- [Now](#now) - Current date/time
- [TimeDeltaWeeks](#timedeltaweeks) - Week time delta
- [TimeDeltaHours](#timedeltahours) - Hour time delta
- [TimeDeltaMinutes](#timedeltaminutes) - Minute time delta
- [TimeDeltaDays](#timedeltadays) - Day time delta

### Trigonometric Functions
- [Sin](#sin) - Sine
- [Cos](#cos) - Cosine
- [Tan](#tan) - Tangent
- [Arcsin](#arcsin) - Arcsine
- [Arccos](#arccos) - Arccosine
- [Arctan](#arctan) - Arctangent
- [Pi](#constants) - Pi constant

### Advanced Functions
- [Map](#map) - Apply function to array elements
- [HasMatchingSublist](#hasmatchingsublist) - Advanced sublist matching

### Integration Functions
- [Function](#function) - Function definition (placeholder)
- [Variable](#variable) - Variable reference
- [TrapezoidalIntegrate](#trapezoidalintegrate) - Numerical integration
