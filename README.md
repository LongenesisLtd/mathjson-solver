# MathJSON Solver

[![Gitter](https://badges.gitter.im/mathjson-solver/community.svg)](https://gitter.im/mathjson-solver/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

_MathJSON Solver_ is a Python module to numerically evaluate MathJSON expressions. It was created by [Longenesis](https://longenesis.com/team) to add numerical evaluation capability of user generated mathematical expressions in Longenesis digital health products and later released as open source project. Its development was inspired by [CortexJS](https://cortexjs.io/compute-engine/) Compute Engine.

Please ask questions and share feedback in our Gitter chat [https://gitter.im/mathjson-solver/community](https://gitter.im/mathjson-solver/community).

## What's new

### 1.4.2
Added `Str` construct. It tries to convert value to string.

### 1.4.0
We changed the behavior of `Average` to be more forgiving. In version 1.4.0 `Average` accepts arrays like `[2, 4 ,"6"]` and internally converts numeric strings to floats.
Also, it skips values that cannot be converted to numeric. Internally `Average` will convert array `[2, "three", 4 ,"6"]` to `[2.0, 4.0 ,6.0]`. When given an empty array, `Average` now returns `None` instead of throwing an error.

## How to use
```python
from mathjson_solver import create_solver

parameters = {"x": 2, "y": 3}
expression = ["Add", "x", "y", 4]

solver = create_solver(parameters)
answer = solver(expression)

print(answer)
# 9, because 2+3+4=9
```

## How to run tests
Make sure you have `pytest` installed. Then `cd` into project directory and run:
```bash
pytest
```

## Contributing Code

We welcome your contributions in the form of pull requests.

1. Fork the repo;
2. Make improvements;
3. Make a pull request to share your improvements with the community and to include it into official release.


## Currently supported constructs
### Math
* `Sum` (alias `Add`)
* `Subtract`
* `Multiply`
* `Divide`
* `Negate`
* `Power`
* `Root`
* `Sqrt`
* `Square`
* `Exp`
* `Log`
* `Log2`
* `Log10`


### Aggregation
* `Array`
* `Max`
* `Min`
* `Average`
* `Median`
* `Len`
* `All`
* `Any`


### Conditions
* `If`
* `Switch`
* `Equal`
* `Greater`
* `GreaterEqual`
* `Less`
* `LessEqual`
* `NotEqual`

### Typecasting
* `Int`
* `Float`

### Additional constructs
* `Constants`


## Examples
```python
["Add", 2, 4, 3]                  # 2+4+3=9
["Subtract", 10, 5, 2]            # 10-5-2=3
["Add", 5, 4, ["Negate", 3]]      # 5+4+(-3)=6
["Multiply", 2, 3, 4]             # 2*3*4=24
["Divide", 10, 5]                 # 10/5=2.0
["Divide", 10, 4]                 # 10/4=2.5
["Power", 2, 3]                   # 2^3=8
["Root", 9, 2]                    # √9=3.0
["Root", 8, 3]                    # ∛8=2.0
["Sqrt", 9]                       # √9=3.0
["Square", 4]                     # 4^2=16
["Exp", 2]                        # e^2≅7.389
["Divide", 10, ["Add", 2+3]]      # 10/(2+3)=10/5=2
["Log", 2.7183]                   # ln(2.7183)≅1.0000
["Log2", 8]                       # log2(8)=3.0
["Log10", 1000]                   # log10(1000)=3.0
["Equal", 10, 10]                 # 10==10 = True
["Equal", 10, 12]                 # 10==10 = False
["Abs", -3.5]                     # |-3.5| = 3.5
["Round", -5.123456, 2]           # -5.12
["Round", -5.123456, 0]           # -5.0
["Round", -5.123456]              # -5
["Array", 1, 2]                   # ["Array", 1, 2]

["Max", ["Array", 1, 2, 3, 5, 2]] # 5
["Max", ["Array", 1, 2, ["Sum", 2, 4, 3], 5, 2]]  # 9
["Median", ["Array", 1, 2, 3, 5, 2]]              # 2
["Average", ["Array", 1, 2, 3, 5, 2]]             # 2.6
["Length", ["Array", 1, 2, 3, 5, 2, 9]]           # 6
["Length", ["Array"]]                             # 0
["Any", ["Array", 0, 0, False, 0, 0]]             # False
["Any", ["Array", 0, 1, False, 0, 0]]             # True
["All", ["Array", 0, 1, False, 0, 0]]             # False
["All", ["Array", 0, 1, False, "", 0]]            # False
["All", ["Array", 2, 1, True, "zz", 2]]           # True
["Int", "12"]                     # 12
["Int", "12.2"]                   # 12
["Float", "12.2"]                 # 12.2
```

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


### If statement
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

Example
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

`If` expression do not need to be strictly _boolean_. Any value that is not _false_ are considered _true_.

### Switch-Case statement
```
["Switch", <on-expression>, <default-result-expression>, [<case1-expression>, <result-expression>], ...],
```

`Switch` construct consists of keyword "Switch" followed by expression whose value will be compared to _Cases'_ values. Then comes the default value. Then follows arbitrary number of _Cases_.

Example  
```python
["Switch", "color", 100, ["red", 10], ["blue", 20], ["green", 30]],
```
The expression in this example will make solver to look for a constant (or a parameter) with the name "color". If "color" is "red", expression evaluates to 10, if "blue" - to 20, if "green" - to 30. Otherwise to 100. Please note that "color" here is a valid expression that evaluates to the actual value of "color" whether it is a parameter or constant.


## Exception handling

A `MathJSONException` is raised when expression cannot be evaluated. Import `MathJSONException` to handle it:
```python
from mathjson_solver import create_solver, MathJSONException

solver = create_solver({})
try:
    solver(["Divide", 1, 0])
except MathJSONException:
    pass
    # invoke your own exception logger here
```

Left unhandled, the exception will look like `MathJSONException("Problem in Divide. ['Divide', 1, 0]. division by zero")`.
