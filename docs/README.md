## Currently supported constructs

<div style="float: left; width: 33%;">

* [Add](#add)
* [Sum](#sum)
* [Negate](#negate)
* [Subtract](#subtract)
* `Constants` -
* [Switch](#switch-case-statement)
* `If` -
* [Multiply](#multiply)
* [Divide](#divide)
* [Power](square-and-power) -
* [Square](square-and-power) -
* [Root](#root-and-square-root)
* [Sqrt](#root-and-square-root)
* [Exp](#exponents-and-logarithms)
* [Log](#exponents-and-logarithms)
* [Log2](#exponents-and-logarithms)
* [Log10](#exponents-and-logarithms)
* [Equal](#equality-greater-than-less-than)
* [StrictEqual](#equality-greater-than-less-than)
* [NotEqual](#equality-greater-than-less-than)
* [Greater](#equality-greater-than-less-than)
* [GreaterEqual](#equality-greater-than-less-than)
* [Less](#equality-greater-than-less-than)
* [LessEqual](#equality-greater-than-less-than)

</div>


<div style="float: left; width: 33%;">

* [Array](#array)
* [Average](#average)
* `Abs` -
* `Round` -
* `Max` -
* `Min` -
* `Median` -
* `Length` -
* `Any` -
* `All` -
* `In` -
* `Not_in` -
* `Contains_any_of` -
* `Contains_all_of` -
* `Contains_none_of` -
* `NotIn` -
* `ContainsAnyOf` -
* `ContainsAllOf` -
* `ContainsNoneOf` -
* `Int` -
* `Float` -
* `Str` -
* `Not` -
* `IsDefined` - Checks if a value is in parameters.

</div>


<div style="float: left; width: 33%;">

* `Map` -
* `HasMatchingSublist` -
* `Strptime` -
* `Strftime` -
* `Today` -
* `Now` -
* `TimeDeltaWeeks` -
* `TimeDeltaHours` -
* `TimeDeltaMinutes` -
* `TimeDeltaDays` -

</div>



## Examples

#### Basic math

#### Add
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



#### Sum
Adds up the given values. `Sum` internally uses `Add` function. Compatible with nested arrays. It is intended that supporting expression builders render `["Sum", 2, 4, 3]` as _∑(2, 4, 3)_.
```python
["Sum", 2, 4, 3]                  # ∑(2, 4, 3)=9
```



#### Negate
Inverts the sign.
```python
["Negate", 3]                     # -(3)=-3
["Negate", -3]                    # -(-3)=3
["Add", 5, 4, ["Negate", 3]]      # 5+4+(-3)=6
```

#### Subtract
Performs basic subtraction.
```python
["Subtract", 10, 5, 2]            # 10-5-2=3
```

#### Multiply
Performs basic multiplication.
```python
["Multiply", 2, 4]                # 2*4=8
["Multiply", 2, 3, 4]             # 2*3*4=24
```

#### Divide
Performs a division.
```python
["Divide", 10, 5]                 # 10/5=2.0
["Divide", 10, 4]                 # 10/4=2.5
["Divide", 1, 3]                  # 1/3=0.33333333333...
```

#### Square and Power
`Power` raises a number to given power. `Square` is a special case of `Power`.
```python
["Power", 2, 3]                   # 2^3=8
["Square", 4]                     # 4^2=16
```

#### Root and square root
```python
["Root", 9, 2]                    # √9=3.0
["Root", 8, 3]                    # ∛8=2.0
["Sqrt", 9]                       # √9=3.0
```

#### Exponents and logarithms
```python
["Exp", 2]                        # e^2≅7.389
["Log", 2.7183]                   # ln(2.7183)≅1.0000
["Log2", 8]                       # log2(8)=3.0
["Log10", 1000]                   # log10(1000)=3.0
```

### Conditionality

#### Equality, greater than, less than
The _mathjson-solver_  provides two comparison operators that require additional explanation: `Equal` and `StrictEqual`, each designed to serve different use cases depending on the required level of strictness in comparisons.

The `Equal` operator is intentionally forgiving, allowing for more flexible comparisons where certain values are treated as equivalent even if they are of different types. For example, `Equal` considers `1` and `"1"` (a string representation of the number) as the same, making it useful in scenarios where type differences are not critical. Additionally, `Equal` treats `False` and `None` as equivalent, which can be beneficial in cases where both represent the absence or falsity of a value.

On the other hand, `StrictEqual` enforces a more precise comparison by considering both the value and type. Under `StrictEqual`, `1` and `"1"` are distinct because one is an integer and the other is a string. Likewise, False and None are treated as separate entities, ensuring that comparisons strictly adhere to data type consistency. This makes `StrictEqual` ideal for cases where exact type matching is necessary to maintain data integrity.

Despite these differences, there are many cases where both `Equal` and `StrictEqual` behave the same way. For instance, they both consider `3.14` equal to `3.14` (as both are identical floating-point numbers) and `"hello"` equal to `"hello"` (since both are the same string). Additionally, for boolean values, both operators treat `True` as equal to `True` and `False` as equal to `False`. These similarities ensure that in most straightforward cases, both operators provide the expected result, while their differences become relevant in edge cases involving type flexibility.

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


### Aggregation

#### Array

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

#### Average

`Average` internally tries to convert strings to numbers, making calculation of average from `[2, 4 ,"6"]` actually possible. Also, it ignores un-convertible elements so arrays like `[2, "three", 4 ,"6"]` don't crash the solver.

```python
["Average", ["Array", 1, 2, 3, 5, 2]]         # 2.6

["Average", ["Array", 2, "three", 4 ,"6"]]    # Average of [2, 4, 6] == 4,  element "three" is ignored

["Average", ["Array"]]                        # None
```



### Other examples
```python
["Abs", -3.5]                     # |-3.5| = 3.5
["Round", -5.123456, 2]           # -5.12
["Round", -5.123456, 0]           # -5.0
["Round", -5.123456]              # -5

["Max", ["Array", 1, 2, 3, 5, 2]] # 5
["Max", ["Array", 1, 2, ["Sum", 2, 4, 3], 5, 2]]  # 9
["Median", ["Array", 1, 2, 3, 5, 2]]              # 2

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
["Str", 12]                       # "12"
["Str", "12"]                     # "12"
["Str", "aabb"]                   # "aabb"
["Not", True]                      # False
["Not", 0]                         # True

["In", 2, ["Array", 1, 2, 3]]     # True
["In", 4, ["Array", 1, 2, 3]]     # False
["ContainsAnyOf", ["Array", 1, 2, 3], ["Array", 3, 4, 5, 6]]     # True
["ContainsAnyOf", ["Array", 1, 2, 3], ["Array", 4, 5, 6]]        # False
["ContainsAllOf", ["Array", 1, 2, 3], ["Array", 1, 2, 3]]        # True
["ContainsAllOf", ["Array", 1, 2], ["Array", 1, 2, 3]]           # False
["Divide", 10, ["Add", 2+3]]      # 10/(2+3)=10/5=2
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

`If` expressions do not need to be strictly _boolean_. Any value that is not _false_ are considered _true_.

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
