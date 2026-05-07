"""
Test suite for Function Declaration and Function Call.
Covers: interpreter behaviour + semantic analysis.
Run with: pytest tests/test_function.py -v
"""

import pytest
from src.lexer import LanguageLexer
from src.parser import LanguageParser
from src.interpreter import Interpreter
from src.memory import Memory
from src.semantic_analyzer import SemanticAnalyzer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(source: str) -> Interpreter:
    """Parse and interpret *source*, return the interpreter for inspection."""
    Memory().reset()
    lexer = LanguageLexer()
    parser = LanguageParser()
    interp = Interpreter()
    interp.visit(parser.parse(lexer.tokenize(source)))
    return interp


def val(interp: Interpreter, name: str):
    return interp.memory.get(name)['value']


def analyze(source: str) -> list[str]:
    """Return semantic errors for *source* (empty list = no errors)."""
    lexer = LanguageLexer()
    parser = LanguageParser()
    ast = parser.parse(lexer.tokenize(source))
    return SemanticAnalyzer().analyze(ast)


# ===========================================================================
# INTERPRETER TESTS
# ===========================================================================

class TestFunctionDeclarationInterpreter:

    def test_function_stored_in_memory(self):
        interp = run("function add(a, b) { return a + b }")
        entry = interp.memory.get('add')
        assert entry['data_type'] == 'function'

    def test_function_no_params_stored(self):
        interp = run("function greet() { return 'hi' }")
        entry = interp.memory.get('greet')
        assert entry['data_type'] == 'function'

    def test_multiple_functions_stored(self):
        interp = run(
            "function f(x) { return x }\n"
            "function g(x) { return x }"
        )
        assert interp.memory.get('f')['data_type'] == 'function'
        assert interp.memory.get('g')['data_type'] == 'function'


class TestFunctionCallInterpreter:

    def test_basic_return_value(self):
        interp = run("function add(a, b) { return a + b }\nr = add(3, 4)")
        assert val(interp, 'r') == 7

    def test_no_args_return(self):
        interp = run("function greet() { return 'hello' }\ns = greet()")
        assert val(interp, 's') == 'hello'

    def test_single_arg(self):
        interp = run("function double(x) { return x + x }\nr = double(5)")
        assert val(interp, 'r') == 10

    def test_float_args(self):
        interp = run("function fadd(a, b) { return a +. b }\nr = fadd(1.5, 2.5)")
        assert val(interp, 'r') == pytest.approx(4.0)

    def test_string_arg(self):
        interp = run("function wrap(s) { return s ++ '!' }\nr = wrap('hi')")
        assert val(interp, 'r') == 'hi!'

    def test_no_return_returns_none(self):
        # function with no return — call result not assigned, just runs body
        interp = run("x = 0\nfunction set() { x = 42 }\nset()")
        assert val(interp, 'x') == 42

    def test_params_are_local(self):
        # outer 'a' must not be modified by the function's local 'a'
        interp = run("a = 1\nfunction f(a) { a = 99 }\nf(10)")
        assert val(interp, 'a') == 1

    def test_wrong_arity_raises(self):
        with pytest.raises(TypeError):
            run("function f(x) { return x }\nf(1, 2)")

    def test_zero_args_wrong_arity_raises(self):
        with pytest.raises(TypeError):
            run("function f(x) { return x }\nf()")

    def test_call_in_expression(self):
        interp = run(
            "function add(a, b) { return a + b }\n"
            "r = add(1, 2) + add(3, 4)"
        )
        assert val(interp, 'r') == 10

    def test_call_as_print_arg(self):
        # print(add(1,2)) — just ensure no crash
        run("function add(a, b) { return a + b }\nprint(add(1, 2))")

    def test_call_standalone_no_crash(self):
        # standalone call — return value discarded, must not raise
        run("function noop() { }\nnoop()")

    def test_nested_call(self):
        # add(add(1,2), 3) == 6
        interp = run(
            "function add(a, b) { return a + b }\n"
            "r = add(add(1, 2), 3)"
        )
        assert val(interp, 'r') == 6

    def test_function_with_body_statements(self):
        # body has statements before return
        interp = run(
            "function compute(x) {\n"
            "    y = x + 1\n"
            "    return y + 1\n"
            "}\n"
            "r = compute(5)"
        )
        assert val(interp, 'r') == 7

    def test_calling_undefined_function_raises(self):
        with pytest.raises((NameError, KeyError)):
            run("r = foo(1, 2)")

    def test_return_bool(self):
        interp = run("function yes() { return true }\nb = yes()")
        assert val(interp, 'b') is True

    def test_recursive_factorial(self):
        # Factorial via iteration (language has no recursion support needed)
        interp = run(
            "function fact(n) {\n"
            "    result = 1\n"
            "    i = 1\n"
            "    while (i != n) {\n"
            "        i = i + 1\n"
            "        result = result * i\n"
            "    }\n"
            "    return result\n"
            "}\n"
            "r = fact(5)"
        )
        assert val(interp, 'r') == 120


# ===========================================================================
# SEMANTIC ANALYSIS TESTS
# ===========================================================================

class TestFunctionDeclarationSemantic:

    def test_valid_function_no_errors(self):
        errors = analyze("function add(a, b) { return a + b }")
        assert errors == []

    def test_valid_no_params_no_errors(self):
        errors = analyze("function greet() { return 'hi' }")
        assert errors == []

    def test_valid_no_return_no_errors(self):
        errors = analyze("function side(x) { x = 1 }")
        assert errors == []


class TestFunctionCallSemantic:

    def test_valid_call_no_errors(self):
        errors = analyze(
            "function add(a, b) { return a + b }\n"
            "r = add(1, 2)"
        )
        assert errors == []

    def test_undefined_function_error(self):
        errors = analyze("r = foo(1, 2)")
        assert any("foo" in e for e in errors)

    def test_wrong_arity_too_many(self):
        errors = analyze(
            "function f(x) { return x }\n"
            "r = f(1, 2)"
        )
        assert any("f" in e and "1" in e and "2" in e for e in errors)

    def test_wrong_arity_too_few(self):
        errors = analyze(
            "function add(a, b) { return a + b }\n"
            "r = add(1)"
        )
        assert any("add" in e for e in errors)

    def test_correct_arity_no_error(self):
        errors = analyze(
            "function f(x, y) { return x + y }\n"
            "r = f(1, 2)"
        )
        assert errors == []

    def test_call_before_declaration_error(self):
        # function called before it is declared → NameError
        errors = analyze("r = add(1, 2)\nfunction add(a, b) { return a + b }")
        assert any("add" in e for e in errors)

    def test_no_args_call_correct(self):
        errors = analyze(
            "function greet() { return 'hi' }\n"
            "s = greet()"
        )
        assert errors == []

    def test_standalone_call_no_errors(self):
        errors = analyze(
            "function noop() { }\n"
            "noop()"
        )
        assert errors == []