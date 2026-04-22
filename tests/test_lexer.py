import pytest
from src.lexer import LanguageLexer


def tokenize(source: str):
    lexer = LanguageLexer()
    return list(lexer.tokenize(source))


def token_types(source: str):
    return [t.type for t in tokenize(source)]


def token_values(source: str):
    return [t.value for t in tokenize(source)]


# --- Integer ---

def test_integer_literal():
    tokens = tokenize("42")
    assert len(tokens) == 1
    assert tokens[0].type == "INTEGER"
    assert tokens[0].value == 42


def test_integer_arithmetic():
    tokens = tokenize("1 + 2 - 3 * 4 / 5")
    assert [(t.type, t.value) for t in tokens] == [
        ("INTEGER", 1), ("INTEGER_ADDITION", "+"), ("INTEGER", 2),
        ("INTEGER_SUBTRACTION", "-"), ("INTEGER", 3),
        ("INTEGER_MULTIPLICATION", "*"), ("INTEGER", 4),
        ("INTEGER_DIVISION", "/"), ("INTEGER", 5),
    ]


def test_integer_uminus():
    tokens = tokenize("--5")
    assert [(t.type, t.value) for t in tokens] == [("INTEGER_UMINUS", "--"), ("INTEGER", 5)]


def test_integer_subtraction_not_swallowed():
    tokens = tokenize("x - 5")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "x"), ("INTEGER_SUBTRACTION", "-"), ("INTEGER", 5)
    ]


def test_integer_equality():
    tokens = tokenize("x == y")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "x"), ("INTEGER_EQUALITY", "=="), ("IDENTIFIER", "y")
    ]


def test_integer_inequality():
    tokens = tokenize("x != y")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "x"), ("INTEGER_INEQUALITY", "!="), ("IDENTIFIER", "y")
    ]


# --- Float ---

def test_float_literal():
    tokens = tokenize("3.14")
    assert len(tokens) == 1
    assert tokens[0].type == "FLOAT"
    assert tokens[0].value == pytest.approx(3.14)


def test_float_arithmetic():
    tokens = tokenize("1.0 +. 2.0 -. 3.0 *. 4.0 /. 5.0")
    assert [(t.type, t.value) for t in tokens] == [
        ("FLOAT", pytest.approx(1.0)), ("FLOAT_ADDITION", "+."), ("FLOAT", pytest.approx(2.0)),
        ("FLOAT_SUBTRACTION", "-."), ("FLOAT", pytest.approx(3.0)),
        ("FLOAT_MULTIPLICATION", "*."), ("FLOAT", pytest.approx(4.0)),
        ("FLOAT_DIVISION", "/."), ("FLOAT", pytest.approx(5.0)),
    ]


def test_float_uminus():
    tokens = tokenize("--. 3.0")
    assert [(t.type, t.value) for t in tokens] == [("FLOAT_UMINUS", "--."), ("FLOAT", pytest.approx(3.0))]


def test_float_subtraction_not_swallowed():
    tokens = tokenize("a -. 1.5")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "a"), ("FLOAT_SUBTRACTION", "-."), ("FLOAT", pytest.approx(1.5))
    ]


def test_float_equality():
    tokens = tokenize("a ==. b")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "a"), ("FLOAT_EQUALITY", "==."), ("IDENTIFIER", "b")
    ]


def test_float_inequality():
    tokens = tokenize("a !=. b")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "a"), ("FLOAT_INEQUALITY", "!=."), ("IDENTIFIER", "b")
    ]


# --- Boolean ---

def test_boolean_true():
    tokens = tokenize("true")
    assert tokens[0].type == "BOOLEAN"
    assert tokens[0].value is True


def test_boolean_false():
    tokens = tokenize("false")
    assert tokens[0].type == "BOOLEAN"
    assert tokens[0].value is False


# --- String ---

def test_string_literal():
    tokens = tokenize("'hello'")
    assert tokens[0].type == "STRING"
    assert tokens[0].value == "hello"


def test_string_concat():
    tokens = tokenize("'a' ++ 'b'")
    assert [(t.type, t.value) for t in tokens] == [
        ("STRING", "a"), ("STRING_CONCAT", "++"), ("STRING", "b")
    ]


# --- Keywords ---

def test_keywords():
    tokens = tokenize("if else while print function return")
    assert [(t.type, t.value) for t in tokens] == [
        ("IF", "if"), ("ELSE", "else"), ("WHILE", "while"),
        ("PRINT", "print"), ("FUNCTION", "function"), ("RETURN", "return"),
    ]


# --- Symbols ---

def test_symbols():
    tokens = tokenize("( ) { } ,")
    assert [(t.type, t.value) for t in tokens] == [
        ("PAREN_OPEN", "("), ("PAREN_CLOSE", ")"),
        ("BRACE_OPEN", "{"), ("BRACE_CLOSE", "}"),
        ("COMMA", ","),
    ]


# --- Identifier & Assignment ---

def test_identifier():
    tokens = tokenize("myVar")
    assert tokens[0].type == "IDENTIFIER"
    assert tokens[0].value == "myVar"


def test_identifier_camel_case():
    for name in ["camelCase", "myLongVariableName", "getValue"]:
        tokens = tokenize(name)
        assert tokens[0].type == "IDENTIFIER"
        assert tokens[0].value == name


def test_identifier_starting_with_keyword():
    for name in ["ifCondition", "whileLoop", "printValue", "returnVal", "trueValue", "falseAlarm"]:
        tokens = tokenize(name)
        assert len(tokens) == 1
        assert tokens[0].type == "IDENTIFIER"
        assert tokens[0].value == name


def test_assignment():
    tokens = tokenize("x = 10")
    assert [(t.type, t.value) for t in tokens] == [
        ("IDENTIFIER", "x"), ("ASSIGNMENT", "="), ("INTEGER", 10)
    ]


# --- Error handling ---

def test_illegal_character_sets_error_flag():
    lexer = LanguageLexer()
    list(lexer.tokenize("@"))
    assert lexer.is_lexical_error is True


def test_valid_input_no_error_flag():
    lexer = LanguageLexer()
    list(lexer.tokenize("x = 10"))
    assert lexer.is_lexical_error is False
