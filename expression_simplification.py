#!/usr/bin/env python3
# Written by Jason Phua
# on 13/10/2024
# Functions to simplify a mathematical expression by
# removing brackets while retaining readability.
# Does not reduce, or combine like terms, therefore leaving
# the full working out of an expression intact.
from type_aliases import *
import re


OPERATOR_PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 0}
ASSOCIATIVE_OPERATORS = "*+"

SINGLE_NUMBER_PATTERN = r'^[\d.]+$'
SIMPLE_OPER_PATTERN = r'^\d+(\.\d+)? [+\-*/] \d+(\.\d+)?$'
COMPLEX_OPER_PATTERN = r'^\d+(\.\d+)?(?: [+\-*/] \d+(\.\d+)?)+$'

OPERATOR_PATTERN = r'[+\-*/]'
PARENTHESES_PATTERN = r'[()]'
INNERMOST_BRACKET_PATTERN = r'\(([^()]+)\)'
OUTER_BRACKET_PATTERN = r'\(([^()]+(?:\([^()]*\))?[^()]+)*\)'

BRACKET_MULT_PATTERN = r'(?<=\))\s\*\s(?=\()'
NOT_MULT_PROCEEDING_BRACKET_PATTERN = r'\)\s[^\*]+\('


# Returns an operation's precedence (PEMDAS/BODMAS priority)
def get_operator_precedence(op: String) -> Integer:
    return OPERATOR_PRECEDENCE.get(op, 0)


# Determines whether a given expression contains redundant parentheses within a given range
def has_redundant_brackets(expr: String, start: Integer, end: Integer) -> Boolean:
    inner = expr[start + 1:end - 1]

    if re.match(SINGLE_NUMBER_PATTERN, inner) or re.match(SIMPLE_OPER_PATTERN, inner) or re.match(COMPLEX_OPER_PATTERN, inner):
        before = expr[:start].strip()
        after = expr[end:].strip()

        inner_operator_match = re.findall(OPERATOR_PATTERN, inner)
        if inner_operator_match:
            inner_operator = inner_operator_match[0]
            if before and before[-1] in OPERATOR_PRECEDENCE:
                before_operator = before[-1]

                if get_operator_precedence(before_operator) > get_operator_precedence(inner_operator):
                    return False

                if before_operator not in ASSOCIATIVE_OPERATORS:
                    return False

            inner_operator = inner_operator_match[-1]
            if after and after[0] in OPERATOR_PRECEDENCE:
                after_operator = after[0]

                if get_operator_precedence(after_operator) > get_operator_precedence(inner_operator):
                    return False

                # Special case: Division will always be bracketed
                if after_operator == '/':
                    return False
        return True

    return False


# Break up a given expression into bracket components
# E.g. (((1 + 2) * (3 + 4)) / 5) returns ['(1 + 2)', '(3 + 4)', '( * )', '( / 5)']
def get_outer_matches(expr: String) -> StringList:
    matches = []
    temp_expr = expr

    while '(' in temp_expr:
        innermost = re.search(OUTER_BRACKET_PATTERN, temp_expr)
        if innermost:
            matches.append(innermost.group(0))
            temp_expr = temp_expr[:innermost.start()] + \
                temp_expr[innermost.end():]
        else:
            break

    return matches


# Extract all operators in an expression into a list
def extract_operators(term: String) -> Integer:
    return re.findall(OPERATOR_PATTERN, term)


# Returns a given expression as a single term
def enclose_parentheses(expr: String, op: String) -> String:
    num_ops = len(extract_operators(expr))
    if num_ops < 1:
        return expr
    if num_ops == 1 and not expr.startswith('(') and not expr.endswith(')'):
        return f"({expr})"
    inner_expr = expr
    if expr.startswith('(') and expr.endswith(')'):
        inner_expr = expr[1:-1]
    if re.search(PARENTHESES_PATTERN, inner_expr):
        # Handle special case: When combining t1 * t2 with '*' and t3,
        # additional brackets are not needed - i.e. (t1 * t2) * t3 is not correct
        if op == '*' and re.search(BRACKET_MULT_PATTERN, expr) and not re.search(NOT_MULT_PROCEEDING_BRACKET_PATTERN, expr):
            return expr
        return f"({expr})"
    return expr


# Account for the distributive property of * and / when combining terms
def combine_terms(prev_inner: String, op: String, new_term: String) -> String:
    distributive_operators = "*/"
    if op in distributive_operators:
        prev_inner = enclose_parentheses(prev_inner, op)
        new_term = enclose_parentheses(new_term, op)
    return f"{prev_inner} {op} {new_term}"


# Join all the terms in a string list into a valid expression,
# removing redundant outer bracket pairs
def recombine_terms(matches: StringList) -> String:
    stack = []
    for term in matches:
        # Push complete terms to the stack
        left_inner = term[1:2]
        right_inner = term[-2:-1]
        if left_inner.isdigit() and right_inner.isdigit():
            stack.append(term)
        # Remove outer brackets of a single term recombination
        # E.g. Recombining '( * 5)' and pops a term and removes outer brackets
        elif left_inner.isdigit():
            left_inner = term[1:-4]
            last_op = extract_operators(term)[-1]
            right_inner = stack.pop()
            stack.append(combine_terms(left_inner, last_op, right_inner))
        elif right_inner.isdigit():
            right_inner = term[4:-1]
            first_op = extract_operators(term)[0]
            left_inner = stack.pop()
            stack.append(combine_terms(left_inner, first_op, right_inner))
        # Recombine an incomplete full expression
        # E.g. Recombine '( * * )' pops three terms and combines
        else:
            inner_operators = extract_operators(term)
            inner_operators.reverse()
            new_term = stack.pop()
            for op in inner_operators:
                prev_inner = stack.pop()
                new_term = combine_terms(prev_inner, op, new_term)
            stack.append(new_term)

    return stack.pop()


# Simplifies the brackets of a given mathematical expression
def simplify_expression(expr: String) -> String:
    while '(' in expr:
        innermost = re.search(INNERMOST_BRACKET_PATTERN, expr)
        if innermost:
            start, end = innermost.span()
            if has_redundant_brackets(expr, start, end):
                expr = expr[:start] + innermost.group(1) + expr[end:]
            else:
                break
    matches = get_outer_matches(expr)

    if len(matches) > 1:
        expr = recombine_terms(matches)
    elif len(matches) == 1 and expr.startswith('(') and expr.endswith(')'):
        expr = expr[1:-1]

    return expr


if __name__ == '__main__':
    # Test expression simplifier
    expr1 = "(((1 + 2) + 3) * 4)"
    expr2 = "(((1 + 2) * 3) + 4)"
    expr3 = "((1 + 2) * (3 + 4))"
    expr4 = "(((1 + 2) * (3 + 4)) / 5)"
    expr5 = "(1 + 2)"
    expr6 = "(((1 + 12) * (3 + 4) * (5 + 6)) / ((1 + 2) * (3 + 4)))"
    expr7 = "(((1 + 12) * (3 + 4) / (5 + 6)) / ((1 + 2) * (3 + 4)))"
    expr8 = "(((1 + 2) * 3) + 4 + 5)"
    expr9 = "((1 - 4) - 5)"
    expr10 = "((5 - (1 - 4))"
    expr11 = "((5 - (1 / 5)) * 5)"
    expr12 = "(((1 / 5) - 5) * 5)"
    expr13 = "(((4 * 1) * 2) * 3)"
    expr14 = "(((22 + 6) / 14) + 8)"
    expr15 = "(2 / 4) / 2"

    print(f'{expr1} -> {simplify_expression(expr1)}')       # (1 + 2 + 3) * 4
    print(f'{expr2} -> {simplify_expression(expr2)}')       # (1 + 2) * 3 + 4
    print(f'{expr3} -> {simplify_expression(expr3)}')       # (1 + 2) * (3 + 4)
    # ((1 + 2) * (3 + 4)) / 5
    print(f'{expr4} -> {simplify_expression(expr4)}')
    print(f'{expr5} -> {simplify_expression(expr5)}')       # 1 + 2

    # ((1 + 12) * (3 + 4) * (5 + 6)) / ((1 + 2) * (3 + 4))
    print(f'{expr6} -> {simplify_expression(expr6)}')
    # ((1 + 12) * ((3 + 4) / (5 + 6))) / ((1 + 2) * (3 + 4))
    print(f'{expr7} -> {simplify_expression(expr7)}')

    # (1 + 2) * 3 + 4 + 5
    print(f'{expr8} -> {simplify_expression(expr8)}')
    print(f'{expr9} -> {simplify_expression(expr9)}')       # 1 - 4 - 5
    print(f'{expr10} -> {simplify_expression(expr10)}')     # 5 - (1 - 4)
    print(f'{expr11} -> {simplify_expression(expr11)}')     # (5 - (1 / 5)) * 5
    print(f'{expr12} -> {simplify_expression(expr12)}')     # ((1 / 5) - 5) * 5
    print(f'{expr13} -> {simplify_expression(expr13)}')     # 4 * 1 * 2 * 3
    print(f'{expr14} -> {simplify_expression(expr14)}')     # (22 + 6) / 14 + 8
    print(f'{expr15} -> {simplify_expression(expr15)}')     # (2 / 4) / 2
