import pytest
from src.lexer import LanguageLexer
from src.parser import LanguageParser
from src.ast.expression import (
    BinaryOp, UnaryOp, FunctionCall, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)
from src.ast.statement import (
    Program, AssignmentStatement, IfStatement, WhileStatement,
    PrintStatement, FunctionDeclaration,
)


def parse(source: str) -> Program:
    return LanguageParser().parse(LanguageLexer().tokenize(source))


# ── Assignment ────────────────────────────────────────────────────────────────

def test_assign_integer():
    tree = parse('x = 42')
    stmt = tree.statements[0]
    assert isinstance(stmt, AssignmentStatement)
    assert stmt.identifier == 'x'
    assert isinstance(stmt.expr, IntegerLiteral)
    assert stmt.expr.value == 42


def test_assign_float():
    tree = parse('f = 3.14')
    stmt = tree.statements[0]
    assert isinstance(stmt.expr, FloatLiteral)
    assert stmt.expr.value == pytest.approx(3.14)


def test_assign_string():
    tree = parse("s = 'hello'")
    stmt = tree.statements[0]
    assert isinstance(stmt.expr, StringLiteral)
    assert stmt.expr.value == 'hello'


def test_assign_bool_true():
    tree = parse('b = true')
    stmt = tree.statements[0]
    assert isinstance(stmt.expr, BooleanLiteral)
    assert stmt.expr.value is True


def test_assign_bool_false():
    tree = parse('b = false')
    stmt = tree.statements[0]
    assert isinstance(stmt.expr, BooleanLiteral)
    assert stmt.expr.value is False


def test_assign_identifier():
    tree = parse('y = x')
    stmt = tree.statements[0]
    assert isinstance(stmt.expr, Identifier)
    assert stmt.expr.name == 'x'


# ── Arithmetic expressions ────────────────────────────────────────────────────

def test_int_binary_ops():
    for op_src, op_sym in [('+', '+'), ('-', '-'), ('*', '*'), ('/', '/')]:
        tree = parse(f'z = 1 {op_src} 2')
        expr = tree.statements[0].expr
        assert isinstance(expr, BinaryOp)
        assert expr.op == op_sym


def test_float_binary_ops():
    for op_src, op_sym in [('+.', '+.'), ('-.', '-.'), ('*.', '*.'), ('/.', '/.')]:
        tree = parse(f'z = 1.0 {op_src} 2.0')
        expr = tree.statements[0].expr
        assert isinstance(expr, BinaryOp)
        assert expr.op == op_sym


def test_string_concat():
    tree = parse("s = 'a' ++ 'b'")
    expr = tree.statements[0].expr
    assert isinstance(expr, BinaryOp)
    assert expr.op == '++'


def test_int_uminus():
    tree = parse('n = -- 5')
    expr = tree.statements[0].expr
    assert isinstance(expr, UnaryOp)
    assert expr.op == '--'
    assert isinstance(expr.operand, IntegerLiteral)


def test_float_uminus():
    tree = parse('n = --. 3.0')
    expr = tree.statements[0].expr
    assert isinstance(expr, UnaryOp)
    assert expr.op == '--.'


def test_precedence_mul_before_add():
    # x = 1 + 2 * 3  →  BinaryOp(+, 1, BinaryOp(*, 2, 3))
    tree = parse('x = 1 + 2 * 3')
    expr = tree.statements[0].expr
    assert isinstance(expr, BinaryOp)
    assert expr.op == '+'
    assert isinstance(expr.right, BinaryOp)
    assert expr.right.op == '*'


def test_parentheses_override_precedence():
    # x = (1 + 2) * 3  →  BinaryOp(*, BinaryOp(+, 1, 2), 3)
    tree = parse('x = (1 + 2) * 3')
    expr = tree.statements[0].expr
    assert isinstance(expr, BinaryOp)
    assert expr.op == '*'
    assert isinstance(expr.left, BinaryOp)
    assert expr.left.op == '+'


# ── Print ─────────────────────────────────────────────────────────────────────

def test_print_identifier():
    tree = parse('print(x)')
    stmt = tree.statements[0]
    assert isinstance(stmt, PrintStatement)
    assert isinstance(stmt.expr, Identifier)
    assert stmt.expr.name == 'x'


def test_print_expression():
    tree = parse('print(1 + 2)')
    stmt = tree.statements[0]
    assert isinstance(stmt.expr, BinaryOp)


# ── If / Else ─────────────────────────────────────────────────────────────────

def test_if_no_else():
    tree = parse('if (x == 0) { print(x) }')
    stmt = tree.statements[0]
    assert isinstance(stmt, IfStatement)
    assert isinstance(stmt.condition, BinaryOp)
    assert stmt.condition.op == '=='
    assert len(stmt.then_body) == 1
    assert isinstance(stmt.then_body[0], PrintStatement)
    assert stmt.else_body is None


def test_if_with_else():
    tree = parse('if (x != 0) { x = 1 } else { x = 0 }')
    stmt = tree.statements[0]
    assert isinstance(stmt, IfStatement)
    assert stmt.else_body is not None
    assert len(stmt.else_body) == 1
    assert isinstance(stmt.else_body[0], AssignmentStatement)


def test_if_condition_inequality():
    tree = parse('if (a != b) { a = 0 }')
    cond = tree.statements[0].condition
    assert isinstance(cond, BinaryOp)
    assert cond.op == '!='


def test_if_condition_float_equality():
    tree = parse('if (a ==. b) { a = 0.0 }')
    cond = tree.statements[0].condition
    assert cond.op == '==.'


def test_if_condition_float_inequality():
    tree = parse('if (a !=. b) { a = 1.0 }')
    cond = tree.statements[0].condition
    assert cond.op == '!=.'


def test_if_condition_bool_identifier():
    tree = parse('if (flag) { x = 1 }')
    cond = tree.statements[0].condition
    assert isinstance(cond, Identifier)
    assert cond.name == 'flag'


def test_if_condition_bool_literal():
    tree = parse('if (true) { x = 1 }')
    cond = tree.statements[0].condition
    assert isinstance(cond, BooleanLiteral)
    assert cond.value is True


def test_if_then_body_multiple_statements():
    tree = parse('if (x == 0) { x = 1 y = 2 }')
    stmt = tree.statements[0]
    assert len(stmt.then_body) == 2


# ── While ─────────────────────────────────────────────────────────────────────

def test_while_basic():
    tree = parse('while (i != 5) { i = i + 1 }')
    stmt = tree.statements[0]
    assert isinstance(stmt, WhileStatement)
    assert isinstance(stmt.condition, BinaryOp)
    assert stmt.condition.op == '!='
    assert len(stmt.body) == 1
    assert isinstance(stmt.body[0], AssignmentStatement)


def test_while_bool_literal_condition():
    tree = parse('while (false) { x = 1 }')
    stmt = tree.statements[0]
    assert isinstance(stmt.condition, BooleanLiteral)
    assert stmt.condition.value is False


def test_while_body_multiple_statements():
    tree = parse('while (x != 0) { x = x - 1 print(x) }')
    stmt = tree.statements[0]
    assert len(stmt.body) == 2


# ── Function declaration ──────────────────────────────────────────────────────

def test_function_no_params_no_return():
    tree = parse('function greet() { print(x) }')
    stmt = tree.statements[0]
    assert isinstance(stmt, FunctionDeclaration)
    assert stmt.name == 'greet'
    assert stmt.params == []
    assert stmt.return_expr is None


def test_function_with_params_and_return():
    tree = parse('function add(a, b) { return a + b }')
    stmt = tree.statements[0]
    assert isinstance(stmt, FunctionDeclaration)
    assert stmt.params == ['a', 'b']
    assert isinstance(stmt.return_expr, BinaryOp)
    assert stmt.return_expr.op == '+'


def test_function_single_param():
    tree = parse('function double(n) { return n * 2 }')
    stmt = tree.statements[0]
    assert stmt.params == ['n']


# ── Function call ─────────────────────────────────────────────────────────────

def test_function_call_no_args():
    tree = parse('x = foo()')
    expr = tree.statements[0].expr
    assert isinstance(expr, FunctionCall)
    assert expr.name == 'foo'
    assert expr.args == []


def test_function_call_with_args():
    tree = parse('x = add(1, 2)')
    expr = tree.statements[0].expr
    assert isinstance(expr, FunctionCall)
    assert expr.name == 'add'
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], IntegerLiteral)
    assert isinstance(expr.args[1], IntegerLiteral)


# ── Program structure ─────────────────────────────────────────────────────────

def test_empty_program():
    tree = parse('')
    assert isinstance(tree, Program)
    assert tree.statements == []


def test_multiple_statements():
    tree = parse('x = 1 y = 2 print(x)')
    assert len(tree.statements) == 3