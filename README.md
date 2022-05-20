# MathJSON Solver

_MathJSON Solver_ is a Python module to numerically evaluate MathJSON expressions. It was created by [Longenesis team](https://longenesis.com/team) to add numerical evaluation capability of user generated mathematical expressions in [Longenesis digital health products](https://longenesis.com/engage). Its development was inspired by [CortexJS Compute Engine](https://cortexjs.io/compute-engine/).

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


## Currently supported MathJSON constructs
* `Add` (alias `Sum`)
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
* `Equal`
* `Greater`
* `GreaterEqual`
* `Less`
* `LessEqual`
* `NotEqual`

### Additional constructs
* `Constants`
* `If`
* `Switch`


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
```

### Constants
```python
[
    "Constants",
    ["constant1", <expression>],
    ["constant2", <expression>],
    ["constant3", <expression>],
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
```python
[
    "If",
    [
        [
            "Equal",
            1,
            0
        ],
        10
    ],
    [
        [
            "Equal",
            2,
            2
        ],
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


### Switch-Case statement
```python
["Switch", <expression>, <expression>, [<expression>, <expression>], ...],
```

`Switch` construct consists of keyword "Switch" followed by expression whose value will be compared to _Cases'_ values. Then comes the default value. Then follows arbitrary number of _Cases_.

Example  
```python
["Switch", "color", 100, ["red", 10], ["blue", 20], ["green", 30]],
```
The expression in this example will make solver to look for a constant (or a parameter) with the name "color". If "color" is "red", expression evaluates to 10, if "blue" - to 20, if "green" - to 30. Otherwise to 100. Please note that "color" here is a valid expression that evaluates to the actual value of "color" whether it is a parameter or constant.
