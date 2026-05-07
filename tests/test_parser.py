"""
pytest test suite for LanguageParser
Run with: pytest test_parser.py -v
"""

import pytest  # noqa


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(source: str):
    """
    Parse *source* and return (result, lexer, parser).
    """
    from parser import parse_program
    return parse_program(source)


def parse_ok(source: str):
    """Parse *source* and assert no errors; return the AST."""
    result, lexer, parser = parse(source)
    assert not lexer.is_lexical_error, "Unexpected lexical error"
    assert not parser.is_syntax_error, "Unexpected syntax error"
    return result


def parse_fail(source: str):
    """Parse *source* and assert at least one error occurred."""
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
        assert ast == ('program', [('assign', 'x', ('integer', 10))])

    def test_integer_addition(self):
        ast = parse_ok("z = 1 + 2")
        stmts = ast[1]
        assert stmts[0] == ('assign', 'z', ('int_add', ('integer', 1), ('integer', 2)))

    def test_integer_subtraction(self):
        ast = parse_ok("z = 5 - 3")
        assert ast[1][0][2] == ('int_sub', ('integer', 5), ('integer', 3))

    def test_integer_multiplication(self):
        ast = parse_ok("z = 4 * 3")
        assert ast[1][0][2] == ('int_mul', ('integer', 4), ('integer', 3))

    def test_integer_division(self):
        ast = parse_ok("z = 8 / 2")
        assert ast[1][0][2] == ('int_div', ('integer', 8), ('integer', 2))

    def test_complex_arithmetic(self):
        # z = x + y - 2 * 4 / 2  —  just check the statement structure
        ast = parse_ok("x = 1\ny = 2\nz = x + y - 2 * 4 / 2")
        assert ast[1][2][0] == 'assign'
        assert ast[1][2][1] == 'z'

    def test_unary_minus(self):
        ast = parse_ok("n = --5")
        outer = ast[1][0][2]
        assert outer[0] == 'int_uminus'
        assert outer[1] == ('integer', 5)

    def test_unary_minus_identifier(self):
        ast = parse_ok("x = 1\nn = --x")
        outer = ast[1][1][2]
        assert outer[0] == 'int_uminus'
        assert outer[1] == ('identifier', 'x')

    def test_unary_minus_expression(self):
        ast = parse_ok("n = --(1 + 2)")
        outer = ast[1][0][2]
        assert outer[0] == 'int_uminus'
        assert outer[1][0] == 'int_add'

    def test_single_minus_invalid(self):
        # Single '-' is not a valid operator in this language
        parse_fail("n = -5")

    def test_identifier_in_expression(self):
        ast = parse_ok("x = 1\ny = x")
        assert ast[1][1][2] == ('identifier', 'x')


# ---------------------------------------------------------------------------
# 2. Float assignment & arithmetic
# ---------------------------------------------------------------------------

class TestFloatAssignment:

    def test_simple_float(self):
        ast = parse_ok("a = 1.5")
        assert ast[1][0] == ('assign', 'a', ('float', 1.5))

    def test_float_addition(self):
        ast = parse_ok("c = 1.0 +. 2.0")
        assert ast[1][0][2] == ('float_add', ('float', 1.0), ('float', 2.0))

    def test_float_subtraction(self):
        ast = parse_ok("c = 3.0 -. 1.0")
        assert ast[1][0][2] == ('float_sub', ('float', 3.0), ('float', 1.0))

    def test_float_multiplication(self):
        ast = parse_ok("c = 2.0 *. 3.0")
        assert ast[1][0][2] == ('float_mul', ('float', 2.0), ('float', 3.0))

    def test_float_division(self):
        ast = parse_ok("c = 6.0 /. 2.0")
        assert ast[1][0][2] == ('float_div', ('float', 6.0), ('float', 2.0))

    def test_float_unary_minus(self):
        ast = parse_ok("d = --. 3.0")
        outer = ast[1][0][2]
        assert outer[0] == 'float_uminus'
        assert outer[1] == ('float', 3.0)

    def test_float_unary_minus_identifier(self):
        ast = parse_ok("a = 1.5\nd = --. a")
        outer = ast[1][1][2]
        assert outer[0] == 'float_uminus'
        assert outer[1] == ('identifier', 'a')

    def test_float_unary_minus_expression(self):
        ast = parse_ok("d = --. (1.0 +. 2.0)")
        outer = ast[1][0][2]
        assert outer[0] == 'float_uminus'
        assert outer[1][0] == 'float_add'

    def test_single_float_minus_invalid(self):
        # Single '-.' is not a valid operator in this language
        parse_fail("d = -. 3.0")

    def test_float_complex_expression(self):
        ast = parse_ok("c = 1.5 +. 2.0 -. 1.0 *. 2.0 /. 1.0")
        assert ast[1][0][1] == 'c'


# ---------------------------------------------------------------------------
# 3. String assignment & concatenation
# ---------------------------------------------------------------------------

class TestStringAssignment:

    def test_simple_string(self):
        ast = parse_ok("s = 'hello'")
        assert ast[1][0] == ('assign', 's', ('string', 'hello'))

    def test_string_concat(self):
        ast = parse_ok("t = 'hello' ++ ' world'")
        expr = ast[1][0][2]
        assert expr == ('string_concat', ('string', 'hello'), ('string', ' world'))

    def test_chained_concat(self):
        ast = parse_ok("t = 'a' ++ 'b' ++ 'c'")
        assert ast[1][0][2][0] == 'string_concat'


# ---------------------------------------------------------------------------
# 4. Boolean assignment
# ---------------------------------------------------------------------------

class TestBooleanAssignment:

    def test_true(self):
        ast = parse_ok("flag = true")
        expr = ast[1][0][2]
        # The lexer emits True (Python bool) as the token value
        assert expr == ('boolean', True)

    def test_false(self):
        ast = parse_ok("flag = false")
        expr = ast[1][0][2]
        assert expr == ('boolean', False)


# ---------------------------------------------------------------------------
# 5. Boolean expressions (comparisons)
# ---------------------------------------------------------------------------

class TestBooleanExpressions:

    def test_int_equality(self):
        ast = parse_ok("x = 1\ny = 2\nif (x == y) { z = 1 }")
        cond = ast[1][2][1]
        assert cond[0] == 'int_eq'
        assert cond[1] == ('identifier', 'x')
        assert cond[2] == ('identifier', 'y')

    def test_int_inequality(self):
        ast = parse_ok("x = 1\ny = 2\nif (x != y) { z = 1 }")
        cond = ast[1][2][1]
        assert cond[0] == 'int_neq'
        assert cond[1] == ('identifier', 'x')
        assert cond[2] == ('identifier', 'y')

    def test_float_equality(self):
        ast = parse_ok("a = 1.0\nb = 2.0\nif (a ==. b) { c = 0.0 }")
        cond = ast[1][2][1]
        assert cond[0] == 'float_eq'
        assert cond[1] == ('identifier', 'a')
        assert cond[2] == ('identifier', 'b')

    def test_float_inequality(self):
        ast = parse_ok("a = 1.0\nb = 2.0\nif (a !=. b) { c = 0.0 }")
        cond = ast[1][2][1]
        assert cond[0] == 'float_neq'
        assert cond[1] == ('identifier', 'a')
        assert cond[2] == ('identifier', 'b')

    def test_bool_literal_condition(self):
        # BooleanExpression → BOOLEAN
        ast = parse_ok("if (true) { x = 1 }")
        cond = ast[1][0][1]
        assert cond == ('boolean', True)

    def test_identifier_condition(self):
        # BooleanExpression → IDENTIFIER
        ast = parse_ok("flag = true\nif (flag) { x = 1 }")
        cond = ast[1][1][1]
        assert cond == ('identifier', 'flag')


# ---------------------------------------------------------------------------
# 6. If / If-Else statements
# ---------------------------------------------------------------------------

class TestIfStatement:

    def test_if_without_else(self):
        src = "if (true) { x = 1 }"
        ast = parse_ok(src)
        stmt = ast[1][0]
        assert stmt[0] == 'if'
        assert stmt[3] is None                          # no else_clause

    def test_if_with_else(self):
        src = "x = 1\ny = 2\nif (x == y) { x = 0 } else { x = 1 }"
        ast = parse_ok(src)
        stmt = ast[1][2]
        assert stmt[0] == 'if'
        assert stmt[3] is not None
        assert stmt[3][0] == 'else'

    def test_if_condition(self):
        src = "if (true) { x = 1 }"
        ast = parse_ok(src)
        stmt = ast[1][0]
        # stmt == ('if', condition, then_body, else_clause)
        assert stmt[1] == ('boolean', True)

    def test_if_body_statements(self):
        src = "if (true) { x = 1\ny = 2 }"
        ast = parse_ok(src)
        body = ast[1][0][2]                             # then_body is a list
        assert len(body) == 2

    def test_else_body_statements(self):
        src = "if (true) { x = 1 } else { x = 2\ny = 3 }"
        ast = parse_ok(src)
        else_clause = ast[1][0][3]                      # ('else', [stmts])
        assert else_clause[0] == 'else'
        assert len(else_clause[1]) == 2

    def test_else_body_content(self):
        src = "if (true) { x = 1 } else { x = 2 }"
        ast = parse_ok(src)
        else_stmts = ast[1][0][3][1]                    # list inside ('else', [...])
        assert else_stmts[0] == ('assign', 'x', ('integer', 2))

    def test_nested_if(self):
        src = "if (true) { if (true) { x = 1 } }"
        ast = parse_ok(src)
        inner = ast[1][0][2][0]                         # first stmt of outer body
        assert inner[0] == 'if'

    def test_if_tuple_length(self):
        # ('if', cond, then_body, else_clause) — always 4 elements
        src = "if (true) { x = 1 }"
        ast = parse_ok(src)
        assert len(ast[1][0]) == 4


# ---------------------------------------------------------------------------
# 7. While statement
# ---------------------------------------------------------------------------

class TestWhileStatement:

    def test_basic_while(self):
        src = "while (true) { x = x + 1 }"
        ast = parse_ok(src)
        stmt = ast[1][0]
        assert stmt[0] == 'while'

    def test_while_condition_bool(self):
        # ('while', condition, body)
        src = "while (true) { x = 1 }"
        ast = parse_ok(src)
        stmt = ast[1][0]
        assert stmt[1] == ('boolean', True)

    def test_while_condition_comparison(self):
        src = "x = 1\ny = 2\nwhile (x == y) { x = x + 1 }"
        ast = parse_ok(src)
        cond = ast[1][2][1]
        assert cond[0] == 'int_eq'

    def test_while_condition_identifier(self):
        # BooleanExpression → IDENTIFIER
        src = "flag = true\nwhile (flag) { x = 1 }"
        ast = parse_ok(src)
        cond = ast[1][1][1]
        assert cond == ('identifier', 'flag')

    def test_while_body(self):
        src = "while (true) { x = 1\ny = 2\nz = 3 }"
        ast = parse_ok(src)
        body = ast[1][0][2]
        assert len(body) == 3

    def test_while_tuple_length(self):
        # ('while', cond, body) — always 3 elements
        src = "while (true) { x = 1 }"
        ast = parse_ok(src)
        assert len(ast[1][0]) == 3


# ---------------------------------------------------------------------------
# 8. Print statement
# ---------------------------------------------------------------------------

class TestPrintStatement:

    def test_print_integer(self):
        ast = parse_ok("print(42)")
        assert ast[1][0] == ('print', ('integer', 42))

    def test_print_string(self):
        ast = parse_ok("print('hello')")
        assert ast[1][0] == ('print', ('string', 'hello'))

    def test_print_expression(self):
        ast = parse_ok("print(1 + 2)")
        stmt = ast[1][0]
        assert stmt[0] == 'print'
        assert stmt[1][0] == 'int_add'

    def test_print_identifier(self):
        ast = parse_ok("x = 5\nprint(x)")
        assert ast[1][1] == ('print', ('identifier', 'x'))

    def test_print_boolean(self):
        ast = parse_ok("print(true)")
        assert ast[1][0] == ('print', ('boolean', True))


# ---------------------------------------------------------------------------
# 9. Function declaration
# ---------------------------------------------------------------------------

class TestFunctionDeclaration:

    def test_simple_function(self):
        src = "function add(p, q) { return p + q }"
        ast = parse_ok(src)
        fn = ast[1][0]
        assert fn[0] == 'function'
        assert fn[1] == 'add'

    def test_function_parameters(self):
        src = "function add(p, q) { return p + q }"
        fn = parse_ok(src)[1][0]
        assert fn[2] == ['p', 'q']

    def test_function_no_params(self):
        src = "function greet() { return 'hi' }"
        fn = parse_ok(src)[1][0]
        assert fn[2] == []

    def test_function_single_param(self):
        src = "function double(x) { return x + x }"
        fn = parse_ok(src)[1][0]
        assert fn[2] == ['x']

    def test_function_return_statement(self):
        src = "function add(p, q) { return p + q }"
        fn = parse_ok(src)[1][0]
        ret = fn[4]
        assert ret is not None
        assert ret[0] == 'return'

    def test_function_return_expression(self):
        src = "function add(p, q) { return p + q }"
        fn = parse_ok(src)[1][0]
        ret = fn[4]
        # ret == ('return', expression)
        assert ret[1][0] == 'int_add'
        assert ret[1][1] == ('identifier', 'p')
        assert ret[1][2] == ('identifier', 'q')

    def test_function_no_return(self):
        src = "function side(x) { x = 1 }"
        fn = parse_ok(src)[1][0]
        assert fn[4] is None

    def test_function_body_statements(self):
        # body (index 3) holds statements BEFORE the return
        src = "function f(x) { x = 1\ny = 2\nreturn x }"
        fn = parse_ok(src)[1][0]
        body = fn[3]
        assert len(body) == 2

    def test_function_tuple_structure(self):
        # ('function', name, params, body_stmts, return_stmt)
        src = "function add(p, q) { return p + q }"
        fn = parse_ok(src)[1][0]
        assert len(fn) == 5


# ---------------------------------------------------------------------------
# 10. Function call
# ---------------------------------------------------------------------------

class TestFunctionCall:

    def test_call_in_assignment(self):
        src = "function add(p, q) { return p + q }\nr = add(1, 2)"
        ast = parse_ok(src)
        call = ast[1][1][2]                             # rhs of 'r = add(1, 2)'
        assert call[0] == 'call'
        assert call[1] == 'add'

    def test_call_arguments(self):
        src = "function add(p, q) { return p + q }\nr = add(1, 2)"
        ast = parse_ok(src)
        args = ast[1][1][2][2]                          # argument list
        assert args == [('integer', 1), ('integer', 2)]

    def test_call_no_args(self):
        src = "function greet() { return 'hi' }\ns = greet()"
        ast = parse_ok(src)
        call = ast[1][1][2]
        assert call[0] == 'call'
        assert call[2] == []

    def test_call_in_print(self):
        src = "function add(p, q) { return p + q }\nprint(add(1, 2))"
        ast = parse_ok(src)
        stmt = ast[1][1]
        assert stmt[0] == 'print'
        assert stmt[1][0] == 'call'

    def test_call_identifier_args(self):
        src = "function add(p, q) { return p + q }\nx = 1\ny = 2\nr = add(x, y)"
        ast = parse_ok(src)
        args = ast[1][3][2][2]
        assert args == [('identifier', 'x'), ('identifier', 'y')]


# ---------------------------------------------------------------------------
# 11. Program-level (multiple statements)
# ---------------------------------------------------------------------------

class TestProgram:

    def test_empty_program(self):
        ast = parse_ok("")
        assert ast == ('program', [])

    def test_multiple_statements(self):
        src = "x = 1\ny = 2\nz = 3"
        ast = parse_ok(src)
        assert len(ast[1]) == 3

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
        assert ast[0] == 'program'
        assert len(ast[1]) > 0

    def test_program_node_tag(self):
        ast = parse_ok("x = 1")
        assert ast[0] == 'program'


# ---------------------------------------------------------------------------
# 12. Syntax error detection
# ---------------------------------------------------------------------------

class TestSyntaxErrors:

    def test_missing_closing_brace(self):
        parse_fail("if (true) { x = 1")

    def test_missing_paren_in_if(self):
        # 'if flag { x = 1 }' — condition not wrapped in parens
        parse_fail("if flag { x = 1 }")

    def test_missing_assignment_value(self):
        parse_fail("x =")

    def test_incomplete_function(self):
        # 'function {}' — missing name and parameter list
        parse_fail("function {}")

    def test_double_assignment_operator(self):
        # 'x == 1' is a comparison expression, not a valid statement
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
        from parser import LanguageParser
        p = LanguageParser()
        assert p.is_syntax_error is False