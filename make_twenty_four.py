#!/usr/bin/env python3
# Written by Jason Phua
# on 13/10/2024
# Much later than the UNSW Winter Workshop in 2022.
# Just bored and noticed extension challenge 7 was
# never finished.
'''
Extension Challenge 7 - Twenty Four
Given 4 integers, determine if 24 is mathematically
reachable using each integer exactly once.
Mathematically reachable means using brackets
and/or any of the basic operators: (+, -, *, /).
We can do this with recursion.

- https://theconfused.me/blog/solving-the-24-game/
- https://theconfused.me/get24/
'''
from type_aliases import *
from expression_simplification import simplify_expression
import re


# Define standard mathematical operators and their associated symbols
OPERATIONS = [
    (lambda a, b: a + b, ' + '),                        # Addition
    (lambda a, b: a - b, ' - '),                        # Subtraction
    (lambda a, b: a * b, ' * '),                        # Multiplication
    (lambda a, b: a / b if b != 0 else None, ' / '),    # Division

    (lambda a, b: b - a, ' - '),                        # Reverse subtraction
    (lambda a, b: b / a if a != 0 else None, ' / ')     # Reverse division
]
NONCOMMUTATIVE_OPS = 4


# Removes an instance of the given element from the given list
def dequeue(list: NumberList, element: Number) -> NumberList:
    list_copy = list.copy()
    if element in list_copy:
        list_copy.remove(element)
    return list_copy


# Concatenates two expressions and an operator within brackets
def combined_expr(left_expr: String, symbol: String, right_expr: String) -> String:
    return f"({left_expr}{symbol}{right_expr})"


def combine_nums(a: Number, b: Number, expr: String) -> CombineNumsReturn:
    results = []
    possible_exprs = []

    for i, (op, symbol) in enumerate(OPERATIONS):
        res = op(a, b)
        if res not in results and res is not None:
            results.append(res)
            new_expr = (combined_expr(expr, symbol, str(b)) if i < NONCOMMUTATIVE_OPS
                        else combined_expr(str(b), symbol, expr))
            possible_exprs.append(new_expr)

    return (results, possible_exprs)


# Attempts to make a target number by combining every given integer
# exactly once with a standard mathematical operator (+, -, *, /)
# Returns both whether it is possible, and adds the solution to the given
# answers list
def make_target_recurse(
    a: Number,
    available: NumberList,
    expr: String,
    answers: StringSet,
    target: Integer
) -> Boolean:
    if a == target and len(available) == 0:
        answers.add(expr)
        return True
    if len(available) == 0:
        return False

    for b in available:
        next_available = dequeue(available, b)
        results, possible_exprs = combine_nums(a, b, expr)
        for r, next_expr in zip(results, possible_exprs):
            if make_target_recurse(r, next_available, next_expr, answers, target):
                return True

    return False


# Pass answers to the simplify_expression function
def parse_answers(answers: StringSet) -> StringSet:
    simplified_answers = set()
    for expr in answers:
        simplified_answers.add(simplify_expression(expr))
    return simplified_answers


# Returns the number of operators and parentheses in an expression
def count_symbols(expr: String) -> Integer:
    basic_operators_pattern = r'[+\-*/^]'
    operator_count = len(re.findall(basic_operators_pattern, expr))
    parentheses_count = expr.count('(') + expr.count(')')
    return operator_count + parentheses_count


# Returns the number of integers matching the order of the input list
def input_similarity(expr: String, input_order: NumberList) -> Integer:
    expr_terms = [n for n in expr.split() if n.isdigit()]
    input_terms = [str(n) for n in input_order]

    matching_order = sum(1 for i, term in enumerate(expr_terms)
                         if term == input_terms[i])
    return matching_order


# Selects the simplest answer from the answers list, prefering
# answers that retain the order of the input list
# The simplest answer has the least parentheses pairs
def select_answer(answers: StringSet, input_order: NumberList) -> String:
    best_answer = min(answers, key=lambda x: (
        count_symbols(x), -input_similarity(x, input_order)))
    return best_answer


# Driver code to run program
def can_make_target(numbers: NumberList, target: Integer = 24) -> Boolean:
    answers = set()
    solved = False
    for start_num in numbers:
        expr = str(start_num)
        available = dequeue(numbers, start_num)
        if make_target_recurse(start_num, available, expr, answers, target):
            solved = True

    given_numbers = ', '.join(map(str, numbers))
    if solved:
        print(f"{target} is reachable using {given_numbers}")
        print(f'Solution: {select_answer(parse_answers(answers), numbers)}')
    else:
        print(f"{target} is not reachable using {given_numbers}")

    return solved


# Test solution:
# 4, 8, 3, 6: True -> (4 + 8) * (6 / 3)
# 1, 5, 5, 5: True -> 5 * (5 - (1/5))
# 3, 9, 4, 10: False
if __name__ == '__main__':
    target = int(input("Enter a target number: "))
    given_nums = input("Enter a list of integers: ").replace(',', ' ').split()
    numbers = [int(x) for x in given_nums]

    print()
    can_make_target(numbers, target)
