"""
pytest test suite for LanguageParser
Run with: pytest test_parser.py -v
"""

import pytest  # noqa

from src.ast_node.expression import (
    BinaryOp, UnaryOp, FunctionCall, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)
from src.ast_node.statement import (
    Program, AssignmentStatement, IfStatement, WhileStatement,
    PrintStatement, FunctionDeclaration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(source: str):
    from src.parser import parse_program
    return parse_program(source)


def parse_ok(source: str):
    result, lexer, parser = parse(source)
    assert not lexer.is_lexical_error, "Unexpected lexical error"
    assert not parser.is_syntax_error, "Unexpected syntax error"
    return result


def parse_fail(source: str):
    result, lexer, parser = parse(source)
    assert lexer.is_lexical_error or parser.is_syntax_error, (
        "Expected a lexical or syntax error, but parsing succeeded"
    )
    return result


# ---------------------------------------------------------------------------
# 1. Integer assignment & arithmetic
# ---------------------------------------------------------------------------

class TestIntegerAssignment:

    def test_simple_integer(self):
        ast = parse_ok("x = 10")
        assert isinstance(ast, Program)
        stmt = ast.statements[0]
        assert isinstance(stmt, AssignmentStatement)
        assert stmt.identifier == 'x'
        assert isinstance(stmt.expr, IntegerLiteral)
        assert stmt.expr.value == 10

    def test_integer_addition(self):
        ast = parse_ok("z = 1 + 2")
        expr = ast.statements[0].expr
        assert isinstance(expr, BinaryOp)
        assert expr.op == '+'
        assert isinstance(expr.left, IntegerLiteral) and expr.left.value == 1
        assert isinstance(expr.right, IntegerLiteral) and expr.right.value == 2

    def test_integer_subtraction(self):
        expr = parse_ok("z = 5 - 3").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '-'
        assert expr.left.value == 5 and expr.right.value == 3

    def test_integer_multiplication(self):
        expr = parse_ok("z = 4 * 3").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '*'
        assert expr.left.value == 4 and expr.right.value == 3

    def test_integer_division(self):
        expr = parse_ok("z = 8 / 2").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '/'
        assert expr.left.value == 8 and expr.right.value == 2

    def test_complex_arithmetic(self):
        ast = parse_ok("x = 1\ny = 2\nz = x + y - 2 * 4 / 2")
        stmt = ast.statements[2]
        assert isinstance(stmt, AssignmentStatement)
        assert stmt.identifier == 'z'

    def test_unary_minus(self):
        expr = parse_ok("n = --5").statements[0].expr
        assert isinstance(expr, UnaryOp)
        assert expr.op == '--'
        assert isinstance(expr.operand, IntegerLiteral)
        assert expr.operand.value == 5

    def test_unary_minus_identifier(self):
        expr = parse_ok("x = 1\nn = --x").statements[1].expr
        assert isinstance(expr, UnaryOp) and expr.op == '--'
        assert isinstance(expr.operand, Identifier)
        assert expr.operand.name == 'x'

    def test_unary_minus_expression(self):
        expr = parse_ok("n = --(1 + 2)").statements[0].expr
        assert isinstance(expr, UnaryOp) and expr.op == '--'
        assert isinstance(expr.operand, BinaryOp) and expr.operand.op == '+'

    def test_single_minus_invalid(self):
        parse_fail("n = -5")

    def test_identifier_in_expression(self):
        expr = parse_ok("x = 1\ny = x").statements[1].expr
        assert isinstance(expr, Identifier)
        assert expr.name == 'x'


# ---------------------------------------------------------------------------
# 2. Float assignment & arithmetic
# ---------------------------------------------------------------------------

class TestFloatAssignment:

    def test_simple_float(self):
        stmt = parse_ok("a = 1.5").statements[0]
        assert isinstance(stmt, AssignmentStatement)
        assert stmt.identifier == 'a'
        assert isinstance(stmt.expr, FloatLiteral)
        assert stmt.expr.value == 1.5

    def test_float_addition(self):
        expr = parse_ok("c = 1.0 +. 2.0").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '+.'
        assert expr.left.value == 1.0 and expr.right.value == 2.0

    def test_float_subtraction(self):
        expr = parse_ok("c = 3.0 -. 1.0").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '-.'
        assert expr.left.value == 3.0 and expr.right.value == 1.0

    def test_float_multiplication(self):
        expr = parse_ok("c = 2.0 *. 3.0").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '*.'
        assert expr.left.value == 2.0 and expr.right.value == 3.0

    def test_float_division(self):
        expr = parse_ok("c = 6.0 /. 2.0").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '/.'
        assert expr.left.value == 6.0 and expr.right.value == 2.0

    def test_float_unary_minus(self):
        expr = parse_ok("d = --. 3.0").statements[0].expr
        assert isinstance(expr, UnaryOp) and expr.op == '--.'
        assert isinstance(expr.operand, FloatLiteral)
        assert expr.operand.value == 3.0

    def test_float_unary_minus_identifier(self):
        expr = parse_ok("a = 1.5\nd = --. a").statements[1].expr
        assert isinstance(expr, UnaryOp) and expr.op == '--.'
        assert isinstance(expr.operand, Identifier)
        assert expr.operand.name == 'a'

    def test_float_unary_minus_expression(self):
        expr = parse_ok("d = --. (1.0 +. 2.0)").statements[0].expr
        assert isinstance(expr, UnaryOp) and expr.op == '--.'
        assert isinstance(expr.operand, BinaryOp) and expr.operand.op == '+.'

    def test_single_float_minus_invalid(self):
        parse_fail("d = -. 3.0")

    def test_float_complex_expression(self):
        stmt = parse_ok("c = 1.5 +. 2.0 -. 1.0 *. 2.0 /. 1.0").statements[0]
        assert stmt.identifier == 'c'
        assert isinstance(stmt.expr, BinaryOp)


# ---------------------------------------------------------------------------
# 3. String assignment & concatenation
# ---------------------------------------------------------------------------

class TestStringAssignment:

    def test_simple_string(self):
        stmt = parse_ok("s = 'hello'").statements[0]
        assert isinstance(stmt, AssignmentStatement)
        assert stmt.identifier == 's'
        assert isinstance(stmt.expr, StringLiteral)
        assert stmt.expr.value == 'hello'

    def test_string_concat(self):
        expr = parse_ok("t = 'hello' ++ ' world'").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '++'
        assert isinstance(expr.left, StringLiteral) and expr.left.value == 'hello'
        assert isinstance(expr.right, StringLiteral) and expr.right.value == ' world'

    def test_chained_concat(self):
        expr = parse_ok("t = 'a' ++ 'b' ++ 'c'").statements[0].expr
        assert isinstance(expr, BinaryOp) and expr.op == '++'


# ---------------------------------------------------------------------------
# 4. Boolean assignment
# ---------------------------------------------------------------------------

class TestBooleanAssignment:

    def test_true(self):
        expr = parse_ok("flag = true").statements[0].expr
        assert isinstance(expr, BooleanLiteral)
        assert expr.value is True

    def test_false(self):
        expr = parse_ok("flag = false").statements[0].expr
        assert isinstance(expr, BooleanLiteral)
        assert expr.value is False


# ---------------------------------------------------------------------------
# 5. Boolean expressions (comparisons)
# ---------------------------------------------------------------------------

class TestBooleanExpressions:

    def test_int_equality(self):
        cond = parse_ok("x = 1\ny = 2\nif (x == y) { z = 1 }").statements[2].condition
        assert isinstance(cond, BinaryOp) and cond.op == '=='
        assert isinstance(cond.left, Identifier) and cond.left.name == 'x'
        assert isinstance(cond.right, Identifier) and cond.right.name == 'y'

    def test_int_inequality(self):
        cond = parse_ok("x = 1\ny = 2\nif (x != y) { z = 1 }").statements[2].condition
        assert isinstance(cond, BinaryOp) and cond.op == '!='
        assert isinstance(cond.left, Identifier) and cond.left.name == 'x'
        assert isinstance(cond.right, Identifier) and cond.right.name == 'y'

    def test_float_equality(self):
        cond = parse_ok("a = 1.0\nb = 2.0\nif (a ==. b) { c = 0.0 }").statements[2].condition
        assert isinstance(cond, BinaryOp) and cond.op == '==.'
        assert isinstance(cond.left, Identifier) and cond.left.name == 'a'
        assert isinstance(cond.right, Identifier) and cond.right.name == 'b'

    def test_float_inequality(self):
        cond = parse_ok("a = 1.0\nb = 2.0\nif (a !=. b) { c = 0.0 }").statements[2].condition
        assert isinstance(cond, BinaryOp) and cond.op == '!=.'
        assert isinstance(cond.left, Identifier) and cond.left.name == 'a'
        assert isinstance(cond.right, Identifier) and cond.right.name == 'b'

    def test_bool_literal_condition(self):
        cond = parse_ok("if (true) { x = 1 }").statements[0].condition
        assert isinstance(cond, BooleanLiteral) and cond.value is True

    def test_identifier_condition(self):
        cond = parse_ok("flag = true\nif (flag) { x = 1 }").statements[1].condition
        assert isinstance(cond, Identifier) and cond.name == 'flag'


# ---------------------------------------------------------------------------
# 6. If / If-Else statements
# ---------------------------------------------------------------------------

class TestIfStatement:

    def test_if_without_else(self):
        stmt = parse_ok("if (true) { x = 1 }").statements[0]
        assert isinstance(stmt, IfStatement)
        assert stmt.else_body is None

    def test_if_with_else(self):
        stmt = parse_ok("x = 1\ny = 2\nif (x == y) { x = 0 } else { x = 1 }").statements[2]
        assert isinstance(stmt, IfStatement)
        assert stmt.else_body is not None
        assert isinstance(stmt.else_body, list)

    def test_if_condition(self):
        stmt = parse_ok("if (true) { x = 1 }").statements[0]
        assert isinstance(stmt.condition, BooleanLiteral)
        assert stmt.condition.value is True

    def test_if_body_statements(self):
        stmt = parse_ok("if (true) { x = 1\ny = 2 }").statements[0]
        assert len(stmt.then_body) == 2

    def test_else_body_statements(self):
        stmt = parse_ok("if (true) { x = 1 } else { x = 2\ny = 3 }").statements[0]
        assert isinstance(stmt.else_body, list)
        assert len(stmt.else_body) == 2

    def test_else_body_content(self):
        stmt = parse_ok("if (true) { x = 1 } else { x = 2 }").statements[0]
        else_stmt = stmt.else_body[0]
        assert isinstance(else_stmt, AssignmentStatement)
        assert else_stmt.identifier == 'x'
        assert isinstance(else_stmt.expr, IntegerLiteral)
        assert else_stmt.expr.value == 2

    def test_nested_if(self):
        stmt = parse_ok("if (true) { if (true) { x = 1 } }").statements[0]
        inner = stmt.then_body[0]
        assert isinstance(inner, IfStatement)

    def test_if_has_condition_then_else(self):
        stmt = parse_ok("if (true) { x = 1 }").statements[0]
        assert hasattr(stmt, 'condition')
        assert hasattr(stmt, 'then_body')
        assert hasattr(stmt, 'else_body')


# ---------------------------------------------------------------------------
# 7. While statement
# ---------------------------------------------------------------------------

class TestWhileStatement:

    def test_basic_while(self):
        stmt = parse_ok("while (true) { x = x + 1 }").statements[0]
        assert isinstance(stmt, WhileStatement)

    def test_while_condition_bool(self):
        stmt = parse_ok("while (true) { x = 1 }").statements[0]
        assert isinstance(stmt.condition, BooleanLiteral)
        assert stmt.condition.value is True

    def test_while_condition_comparison(self):
        stmt = parse_ok("x = 1\ny = 2\nwhile (x == y) { x = x + 1 }").statements[2]
        assert isinstance(stmt.condition, BinaryOp)
        assert stmt.condition.op == '=='

    def test_while_condition_identifier(self):
        stmt = parse_ok("flag = true\nwhile (flag) { x = 1 }").statements[1]
        assert isinstance(stmt.condition, Identifier)
        assert stmt.condition.name == 'flag'

    def test_while_body(self):
        stmt = parse_ok("while (true) { x = 1\ny = 2\nz = 3 }").statements[0]
        assert len(stmt.body) == 3

    def test_while_has_condition_and_body(self):
        stmt = parse_ok("while (true) { x = 1 }").statements[0]
        assert hasattr(stmt, 'condition')
        assert hasattr(stmt, 'body')


# ---------------------------------------------------------------------------
# 8. Print statement
# ---------------------------------------------------------------------------

class TestPrintStatement:

    def test_print_integer(self):
        stmt = parse_ok("print(42)").statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expr, IntegerLiteral)
        assert stmt.expr.value == 42

    def test_print_string(self):
        stmt = parse_ok("print('hello')").statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expr, StringLiteral)
        assert stmt.expr.value == 'hello'

    def test_print_expression(self):
        stmt = parse_ok("print(1 + 2)").statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expr, BinaryOp) and stmt.expr.op == '+'

    def test_print_identifier(self):
        stmt = parse_ok("x = 5\nprint(x)").statements[1]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expr, Identifier) and stmt.expr.name == 'x'

    def test_print_boolean(self):
        stmt = parse_ok("print(true)").statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expr, BooleanLiteral) and stmt.expr.value is True


# ---------------------------------------------------------------------------
# 9. Function declaration
# ---------------------------------------------------------------------------

class TestFunctionDeclaration:

    def test_simple_function(self):
        fn = parse_ok("function add(p, q) { return p + q }").statements[0]
        assert isinstance(fn, FunctionDeclaration)
        assert fn.name == 'add'

    def test_function_parameters(self):
        fn = parse_ok("function add(p, q) { return p + q }").statements[0]
        assert fn.params == ['p', 'q']

    def test_function_no_params(self):
        fn = parse_ok("function greet() { return 'hi' }").statements[0]
        assert fn.params == []

    def test_function_single_param(self):
        fn = parse_ok("function double(x) { return x + x }").statements[0]
        assert fn.params == ['x']

    def test_function_return_expression(self):
        fn = parse_ok("function add(p, q) { return p + q }").statements[0]
        ret = fn.return_expr
        assert isinstance(ret, BinaryOp) and ret.op == '+'
        assert isinstance(ret.left, Identifier) and ret.left.name == 'p'
        assert isinstance(ret.right, Identifier) and ret.right.name == 'q'

    def test_function_no_return(self):
        fn = parse_ok("function side(x) { x = 1 }").statements[0]
        assert fn.return_expr is None

    def test_function_body_statements(self):
        fn = parse_ok("function f(x) { x = 1\ny = 2\nreturn x }").statements[0]
        assert len(fn.body) == 2

    def test_function_has_fields(self):
        fn = parse_ok("function add(p, q) { return p + q }").statements[0]
        assert hasattr(fn, 'name')
        assert hasattr(fn, 'params')
        assert hasattr(fn, 'body')
        assert hasattr(fn, 'return_expr')


# ---------------------------------------------------------------------------
# 10. Function call
# ---------------------------------------------------------------------------

class TestFunctionCall:

    def test_call_in_assignment(self):
        ast = parse_ok("function add(p, q) { return p + q }\nr = add(1, 2)")
        call = ast.statements[1].expr
        assert isinstance(call, FunctionCall)
        assert call.name == 'add'

    def test_call_arguments(self):
        ast = parse_ok("function add(p, q) { return p + q }\nr = add(1, 2)")
        args = ast.statements[1].expr.args
        assert len(args) == 2
        assert isinstance(args[0], IntegerLiteral) and args[0].value == 1
        assert isinstance(args[1], IntegerLiteral) and args[1].value == 2

    def test_call_no_args(self):
        ast = parse_ok("function greet() { return 'hi' }\ns = greet()")
        call = ast.statements[1].expr
        assert isinstance(call, FunctionCall)
        assert call.args == []

    def test_call_in_print(self):
        ast = parse_ok("function add(p, q) { return p + q }\nprint(add(1, 2))")
        stmt = ast.statements[1]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expr, FunctionCall)

    def test_call_identifier_args(self):
        ast = parse_ok("function add(p, q) { return p + q }\nx = 1\ny = 2\nr = add(x, y)")
        args = ast.statements[3].expr.args
        assert isinstance(args[0], Identifier) and args[0].name == 'x'
        assert isinstance(args[1], Identifier) and args[1].name == 'y'


# ---------------------------------------------------------------------------
# 11. Program-level (multiple statements)
# ---------------------------------------------------------------------------

class TestProgram:

    def test_empty_program(self):
        ast = parse_ok("")
        assert isinstance(ast, Program)
        assert ast.statements == []

    def test_multiple_statements(self):
        ast = parse_ok("x = 1\ny = 2\nz = 3")
        assert len(ast.statements) == 3

    def test_full_program(self):
        src = """
            x = 10
            y = 3
            z = x + y - 2 * 4 / 2
            n = --5
            a = 1.5
            b = 2.0
            c = a +. b -. 1.0 *. 2.0 /. 1.0
            d = --. 3.0
            flag = true
            flag2 = false
            s = 'hello'
            t = 'hello' ++ ' world'
            if (x == y) { x = 0 } else { x = 1 }
            if (a ==. b) { a = 0.0 }
            if (x != y) { x = 99 }
            if (a !=. b) { a = 99.0 }
            while (true) { x = x + 1 }
            print(z)
            print(s)
            function add(p, q) { return p + q }
        """
        ast = parse_ok(src)
        assert isinstance(ast, Program)
        assert len(ast.statements) > 0

    def test_program_is_program_node(self):
        ast = parse_ok("x = 1")
        assert isinstance(ast, Program)


# ---------------------------------------------------------------------------
# 12. Syntax error detection
# ---------------------------------------------------------------------------

class TestSyntaxErrors:

    def test_missing_closing_brace(self):
        parse_fail("if (true) { x = 1")

    def test_missing_paren_in_if(self):
        parse_fail("if flag { x = 1 }")

    def test_missing_assignment_value(self):
        parse_fail("x =")

    def test_incomplete_function(self):
        parse_fail("function {}")

    def test_double_assignment_operator(self):
        parse_fail("x == 1")

    def test_is_syntax_error_flag_set(self):
        _, _, parser = parse("if flag { x = 1 }")
        assert parser.is_syntax_error

    def test_missing_while_paren(self):
        parse_fail("while true { x = 1 }")

    def test_missing_function_name(self):
        parse_fail("function () { return 1 }")


# ---------------------------------------------------------------------------
# 13. Parser initialisation
# ---------------------------------------------------------------------------

class TestParserInit:

    def test_is_syntax_error_starts_false(self):
        from src.parser import LanguageParser
        p = LanguageParser()
        assert p.is_syntax_error is False