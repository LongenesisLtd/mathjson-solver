# MathJSON Solver

[![PyPI](https://img.shields.io/pypi/v/mathjson-solver.svg)](https://pypi.org/project/mathjson-solver/)
[![PyPI Downloads](https://static.pepy.tech/badge/mathjson-solver/month)](https://pepy.tech/projects/mathjson-solver)
![Coverage](https://img.shields.io/badge/coverage-91-green)

_MathJSON Solver_ is a Python module to numerically evaluate MathJSON expressions, like `["Add", 1, 2]`. It is developed by [Longenesis](https://longenesis.com/team) to enable numerical evaluation of user provided mathematical expressions in Longenesis digital health products. Its development was inspired by [CortexJS](https://cortexjs.io/compute-engine/) Compute Engine.

Please ask questions and share feedback in our Gitter chat [https://gitter.im/mathjson-solver/community](https://gitter.im/mathjson-solver/community).
[![Gitter](https://badges.gitter.im/mathjson-solver/community.svg)](https://gitter.im/mathjson-solver/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

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

## Currently supported constructs
Find the full list of supported constructs in the [docs/README.md](https://github.com/LongenesisLtd/mathjson-solver/blob/main/docs/README.md).


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


## How to run tests
Make sure you have `pytest` installed. Then `cd` into project directory and run:
```bash
pytest
```
