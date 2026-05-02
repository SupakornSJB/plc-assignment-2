import pytest
from parser import MyLexer, MyParser

lexer = MyLexer()
parser = MyParser()


def parse(input_text):
    tokens = lexer.tokenize(input_text)
    return parser.parse(tokens)


def test_integer():
    assert parse("5") == ('int', '5')


def test_float():
    assert parse("5.2") == ('float', '5.2')


def test_string():
    assert parse('"hi"') == ('string', '"hi"')


def test_boolean_true():
    assert parse("true") == ('bool', 'true')


def test_identifier():
    assert parse("x") == ('var', 'x')

def test_simple_add():
    assert parse("a + b") == ('+', ('var', 'a'), ('var', 'b'))


def test_simple_mul():
    assert parse("a * b") == ('*', ('var', 'a'), ('var', 'b'))


def test_float_add():
    assert parse("a +. b") == ('+.', ('var', 'a'), ('var', 'b'))


def test_concat():
    assert parse("a ++ b") == ('++', ('var', 'a'), ('var', 'b'))

def test_mul_over_add():
    assert parse("a + b * c") == (
        '+',
        ('var', 'a'),
        ('*', ('var', 'b'), ('var', 'c'))
    )


def test_mul_chain():
    assert parse("a * b + c * d") == (
        '+',
        ('*', ('var', 'a'), ('var', 'b')),
        ('*', ('var', 'c'), ('var', 'd'))
    )


def test_float_precedence():
    assert parse("a + b *. c") == (
        '+',
        ('var', 'a'),
        ('*.', ('var', 'b'), ('var', 'c'))
    )

def test_left_assoc_add():
    assert parse("a + b + c") == (
        '+',
        ('+', ('var', 'a'), ('var', 'b')),
        ('var', 'c')
    )


def test_left_assoc_mul():
    assert parse("a * b * c") == (
        '*',
        ('*', ('var', 'a'), ('var', 'b')),
        ('var', 'c')
    )

def test_unary_minus():
    assert parse("-a") == ('neg', ('var', 'a'))


def test_double_unary():
    assert parse("--a") == ('neg', ('neg', ('var', 'a')))


def test_unary_with_expr():
    assert parse("-(a + b)") == (
        'neg',
        ('+', ('var', 'a'), ('var', 'b'))
    )

def test_parentheses_override():
    assert parse("(a + b) * c") == (
        '*',
        ('+', ('var', 'a'), ('var', 'b')),
        ('var', 'c')
    )


def test_nested_parentheses():
    assert parse("((a))") == ('var', 'a')


def test_eq():
    assert parse("a == b") == ('==', ('var', 'a'), ('var', 'b'))


def test_neq():
    assert parse("a != b") == ('!=', ('var', 'a'), ('var', 'b'))


def test_float_eq():
    assert parse("a ==. b") == ('==.', ('var', 'a'), ('var', 'b'))


def test_comparison_precedence():
    assert parse("a + b == c") == (
        '==',
        ('+', ('var', 'a'), ('var', 'b')),
        ('var', 'c')
    )


def test_assignment():
    assert parse("x = a + b") == [
        ('assign', 'x', ('+', ('var', 'a'), ('var', 'b')))
    ]


def test_multiple_statements():
    assert parse("x = 1 y = 2") == [
        ('assign', 'x', ('int', '1')),
        ('assign', 'y', ('int', '2'))
    ]


def test_print():
    assert parse("print(a)") == [
        ('print', ('var', 'a'))
    ]

def test_if():
    assert parse("if (a) { x = 1 }") == [
        ('if',
         ('var', 'a'),
         [('assign', 'x', ('int', '1'))],
         None)
    ]


def test_if_else():
    assert parse("if (a) { x = 1 } else { x = 2 }") == [
        ('if',
         ('var', 'a'),
         [('assign', 'x', ('int', '1'))],
         [('assign', 'x', ('int', '2'))])
    ]


def test_while():
    assert parse("while (a) { x = 1 }") == [
        ('while',
         ('var', 'a'),
         [('assign', 'x', ('int', '1'))])
    ]


def test_function_no_params():
    assert parse("function f() { return 1 }") == [
        ('func', 'f', [], [], ('int', '1'))
    ]


def test_function_with_params():
    assert parse("function f(a,b) { return a }") == [
        ('func', 'f', ['a', 'b'], [], ('var', 'a'))
    ]


def test_function_body():
    assert parse("function f() { x = 1 return x }") == [
        ('func',
         'f',
         [],
         [('assign', 'x', ('int', '1'))],
         ('var', 'x'))
    ]


def test_complex_expr():
    assert parse("a + b * c == d") == (
        '==',
        ('+', ('var', 'a'), ('*', ('var', 'b'), ('var', 'c'))),
        ('var', 'd')
    )


def test_mixed_ops():
    assert parse("a ++ b + c") == (
        '+',
        ('++', ('var', 'a'), ('var', 'b')),
        ('var', 'c')
    )


def test_chain_all():
    assert parse("a + b * c + d") == (
        '+',
        ('+', ('var', 'a'),
         ('*', ('var', 'b'), ('var', 'c'))),
        ('var', 'd')
    )
