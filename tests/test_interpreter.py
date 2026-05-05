import pytest
from src.lexer import LanguageLexer
from src.parser import LanguageParser
from src.interpreter import Interpreter
from src.memory import Memory


def run(source: str) -> Interpreter:
    """Parse and interpret source, return the interpreter so tests can inspect memory."""
    # Memory is a singleton — reset its scopes between tests
    mem = Memory()
    mem.scopes = [{}]

    lexer = LanguageLexer()
    parser = LanguageParser()
    interp = Interpreter()
    interp.visit(parser.parse(lexer.tokenize(source)))
    return interp


def val(interp: Interpreter, name: str):
    return interp.memory.get(name)['value']

def test_assign_integer():
    interp = run('x = 42')
    assert val(interp, 'x') == 42

def test_assign_float():
    interp = run('f = 3.14')
    assert val(interp, 'f') == pytest.approx(3.14)

def test_assign_string():
    interp = run("s = 'hello'")
    assert val(interp, 's') == 'hello'

def test_assign_bool():
    interp = run('b = true')
    assert val(interp, 'b') is True

def test_assign_expression():
    interp = run('x = 2 + 3 * 4')
    assert val(interp, 'x') == 14     # precedence: 3*4 first

def test_int_addition():
    assert val(run('x = 3 + 4'), 'x') == 7

def test_int_subtraction():
    assert val(run('x = 10 - 3'), 'x') == 7

def test_int_multiplication():
    assert val(run('x = 3 * 4'), 'x') == 12

def test_int_division():
    assert val(run('x = 10 / 3'), 'x') == 3   # integer (floor) division

def test_float_addition():
    assert val(run('x = 1.5 +. 2.5'), 'x') == pytest.approx(4.0)

def test_float_division():
    assert val(run('x = 7.0 /. 2.0'), 'x') == pytest.approx(3.5)

def test_string_concat():
    assert val(run("s = 'hello' ++ ' world'"), 's') == 'hello world'

def test_int_uminus():
    assert val(run('x = -- 5'), 'x') == -5

def test_float_uminus():
    assert val(run('x = --. 3.0'), 'x') == pytest.approx(-3.0)

def test_if_taken():
    interp = run('x = 1\nif (x == 1) { x = 99 }')
    assert val(interp, 'x') == 99

def test_if_not_taken():
    interp = run('x = 2\nif (x == 1) { x = 99 }')
    assert val(interp, 'x') == 2

def test_else_taken():
    interp = run('x = 5\nif (x == 1) { x = 10 } else { x = 20 }')
    assert val(interp, 'x') == 20

def test_else_not_taken():
    interp = run('x = 1\nif (x == 1) { x = 10 } else { x = 20 }')
    assert val(interp, 'x') == 10

def test_if_inequality():
    interp = run('x = 5\nif (x != 3) { x = 0 }')
    assert val(interp, 'x') == 0

def test_if_float_equality():
    interp = run('x = 1\nif (1.0 ==. 1.0) { x = 7 }')
    assert val(interp, 'x') == 7

def test_if_float_inequality():
    interp = run('x = 0\nif (1.0 !=. 2.0) { x = 1 }')
    assert val(interp, 'x') == 1

def test_if_bool_identifier_true():
    interp = run('flag = true\nx = 0\nif (flag) { x = 1 }')
    assert val(interp, 'x') == 1

def test_if_bool_identifier_false():
    interp = run('flag = false\nx = 0\nif (flag) { x = 1 }')
    assert val(interp, 'x') == 0

def test_if_condition_non_bool_raises():
    with pytest.raises(TypeError):
        run('x = 5\nif (x) { x = 0 }')

def test_while_counts_to_five():
    interp = run('i = 0\nwhile (i != 5) { i = i + 1 }')
    assert val(interp, 'i') == 5

def test_while_body_not_entered_when_false():
    interp = run('x = 10\nwhile (false) { x = 99 }')
    assert val(interp, 'x') == 10

def test_while_accumulates():
    interp = run('s = 0\ni = 1\nwhile (i != 4) { s = s + i\ni = i + 1 }')
    assert val(interp, 's') == 6    # 1+2+3

def test_while_condition_non_bool_raises():
    with pytest.raises(TypeError):
        run('x = 5\nwhile (x) { x = x - 1 }')

def test_function_return_value():
    interp = run('function add(a, b) { return a + b }\nr = add(3, 4)')
    assert val(interp, 'r') == 7

def test_function_no_return():
    interp = run('x = 0\nfunction set() { x = 42 }\nset()')
    assert val(interp, 'x') == 42

def test_function_params_are_local():
    interp = run('a = 1\nfunction f(a) { a = 99 }\nf(10)')
    assert val(interp, 'a') == 1

def test_function_wrong_arity_raises():
    with pytest.raises(TypeError):
        run('function f(x) { return x }\nf(1, 2)')

def test_int_op_with_float_raises():
    with pytest.raises(TypeError):
        run('x = 1 + 2.0')

def test_int_op_with_string_raises():
    with pytest.raises(TypeError):
        run("x = 1 + 'hello'")

def test_int_op_with_bool_raises():
    with pytest.raises(TypeError):
        run('x = 1 + true')

def test_float_op_with_int_raises():
    with pytest.raises(TypeError):
        run('x = 1.0 +. 2')

def test_float_op_with_string_raises():
    with pytest.raises(TypeError):
        run("x = 1.0 +. 'hello'")

def test_string_op_with_int_raises():
    with pytest.raises(TypeError):
        run("x = 'hello' ++ 1")

def test_string_op_with_float_raises():
    with pytest.raises(TypeError):
        run("x = 'hello' ++ 1.0")

def test_int_equality_with_float_raises():
    with pytest.raises(TypeError):
        run('if (1 == 1.0) { x = 1 }')

def test_float_equality_with_int_raises():
    with pytest.raises(TypeError):
        run('if (1.0 ==. 1) { x = 1 }')

def test_unary_int_neg_on_float_raises():
    with pytest.raises(TypeError):
        run('x = -- 1.0')

def test_unary_float_neg_on_int_raises():
    with pytest.raises(TypeError):
        run('x = --. 1')


def test_fibonacci_iterative():
    source = '''
        a = 0
        b = 1
        n = 8
        i = 0
        while (i != n) {
            tmp = a + b
            a = b
            b = tmp
            i = i + 1
        }
    '''
    interp = run(source)
    assert val(interp, 'a') == 21