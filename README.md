# Make-24 Solver

A recursive solver for the classic "Make 24" puzzle.

Given a set of integers, the solver determines whether a target number can be reached by using every input exactly once, with the basic arithmetic operators:

- Addition (`+`)
- Subtraction (`-`)
- Multiplication (`*`)
- Division (`/`)

Parentheses may be used to control the order of operations.

For example, given:

```text
1 2 3 4
````

the solver searches for an expression using each number exactly once that evaluates to the target.

## Generalisation

Although the original puzzle uses four integers and a target of 24, the solver is configurable:

* Any number of input integers can be provided.
* Any target value can be specified.

This makes the program a general arithmetic-expression reachability solver rather than being limited to the traditional Make-24 puzzle.

## Approach

The solver uses recursive search to explore possible combinations of numbers and arithmetic operations.

At each step, two available values are selected, combined using an arithmetic operator, and replaced with the resulting value. The process continues until only one value remains.

This allows the solver to explore different orderings, operators, and parenthesisations without having to explicitly enumerate every possible expression structure.

## Expression Simplification

The repository also contains `expression_simplification.py`, which simplifies generated mathematical expressions by removing unnecessary parentheses without combining or reducing terms.

This is used to produce readable solutions when the solver finds an expression that reaches the target.

For example, an internally generated expression such as:

```text
((1 + 2) * (3 + 4))
```

can be simplified to a more readable form where parentheses are not required.

The simplifier operates on the expression structure rather than evaluating or algebraically reducing the expression, allowing the original operations and terms to remain visible.

## Example

The solver can be used to answer questions such as:

```text
Input:  1 2 3 4
Target: 24

Possible solution:
(1 + 3) * (2 + 4) = 24
```

The same solver can be used with different numbers of inputs and different target values, but will only output the first solution it finds.
