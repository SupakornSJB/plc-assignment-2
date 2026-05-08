from src.ast_node.statement import (
    Program,
    AssignmentStatement,
    IfStatement,
    WhileStatement,
    PrintStatement,
    FunctionDeclaration,
)
from src.ast_node.expression import (
    BinaryOp,
    UnaryOp,
    FunctionCall,
    Identifier,
    IntegerLiteral,
    FloatLiteral,
    StringLiteral,
    BooleanLiteral,
)


# ── Literals ──────────────────────────────────────────────────────────────────

def test_integer_literal():
    node = IntegerLiteral(42)
    assert node.value == 42


def test_float_literal():
    node = FloatLiteral(3.14)
    assert node.value == 3.14


def test_string_literal():
    node = StringLiteral("hello")
    assert node.value == "hello"


def test_boolean_literal_true():
    node = BooleanLiteral(True)
    assert node.value is True


def test_boolean_literal_false():
    node = BooleanLiteral(False)
    assert node.value is False


# ── Identifier ────────────────────────────────────────────────────────────────

def test_identifier():
    node = Identifier("x")
    assert node.name == "x"


# ── BinaryOp ──────────────────────────────────────────────────────────────────

def test_binary_op_int_add():
    node = BinaryOp("+", IntegerLiteral(1), IntegerLiteral(2))
    assert node.op == "+"
    assert isinstance(node.left, IntegerLiteral)
    assert isinstance(node.right, IntegerLiteral)


def test_binary_op_float_add():
    node = BinaryOp("+.", FloatLiteral(1.0), FloatLiteral(2.0))
    assert node.op == "+."


def test_binary_op_string_concat():
    node = BinaryOp("++", StringLiteral("a"), StringLiteral("b"))
    assert node.op == "++"


def test_binary_op_int_equality():
    node = BinaryOp("==", Identifier("x"), IntegerLiteral(0))
    assert node.op == "=="


def test_binary_op_float_equality():
    node = BinaryOp("==.", FloatLiteral(1.0), FloatLiteral(1.0))
    assert node.op == "==."


def test_binary_op_int_inequality():
    node = BinaryOp("!=", Identifier("x"), IntegerLiteral(0))
    assert node.op == "!="


def test_binary_op_float_inequality():
    node = BinaryOp("!=.", FloatLiteral(1.0), FloatLiteral(2.0))
    assert node.op == "!=."


def test_binary_op_all_int_ops():
    for op in ("+", "-", "*", "/"):
        node = BinaryOp(op, IntegerLiteral(1), IntegerLiteral(2))
        assert node.op == op


def test_binary_op_all_float_ops():
    for op in ("+.", "-.", "*.", "/."):
        node = BinaryOp(op, FloatLiteral(1.0), FloatLiteral(2.0))
        assert node.op == op


# ── UnaryOp ───────────────────────────────────────────────────────────────────

def test_unary_op_int_neg():
    node = UnaryOp("--", IntegerLiteral(5))
    assert node.op == "--"
    assert isinstance(node.operand, IntegerLiteral)


def test_unary_op_float_neg():
    node = UnaryOp("--.", FloatLiteral(3.0))
    assert node.op == "--."
    assert isinstance(node.operand, FloatLiteral)


# ── FunctionCall ──────────────────────────────────────────────────────────────

def test_function_call_no_args():
    node = FunctionCall("foo", [])
    assert node.name == "foo"
    assert node.args == []


def test_function_call_with_args():
    args = [IntegerLiteral(1), Identifier("x")]
    node = FunctionCall("add", args)
    assert node.name == "add"
    assert len(node.args) == 2
    assert isinstance(node.args[0], IntegerLiteral)
    assert isinstance(node.args[1], Identifier)


# ── AssignmentStatement ───────────────────────────────────────────────────────

def test_assignment_statement():
    node = AssignmentStatement("x", IntegerLiteral(10))
    assert node.identifier == "x"
    assert isinstance(node.expr, IntegerLiteral)
    assert node.expr.value == 10


# ── PrintStatement ────────────────────────────────────────────────────────────

def test_print_statement():
    node = PrintStatement(Identifier("x"))
    assert isinstance(node.expr, Identifier)
    assert node.expr.name == "x"


# ── IfStatement ───────────────────────────────────────────────────────────────

def test_if_statement_no_else():
    cond = BinaryOp("==", Identifier("x"), IntegerLiteral(0))
    body = [PrintStatement(Identifier("x"))]
    node = IfStatement(cond, body, None)
    assert node.condition is cond
    assert node.then_body == body
    assert node.else_body is None


def test_if_statement_with_else():
    cond = BinaryOp("!=", Identifier("x"), IntegerLiteral(0))
    then_body = [AssignmentStatement("x", IntegerLiteral(1))]
    else_body = [AssignmentStatement("x", IntegerLiteral(0))]
    node = IfStatement(cond, then_body, else_body)
    assert node.else_body == else_body


# ── WhileStatement ────────────────────────────────────────────────────────────

def test_while_statement():
    cond = BooleanLiteral(True)
    body = [AssignmentStatement("x", BinaryOp("+", Identifier("x"), IntegerLiteral(1)))]
    node = WhileStatement(cond, body)
    assert node.condition is cond
    assert len(node.body) == 1


# ── FunctionDeclaration ───────────────────────────────────────────────────────

def test_function_declaration_no_return():
    body = [PrintStatement(Identifier("x"))]
    node = FunctionDeclaration("foo", ["x"], body, None)
    assert node.name == "foo"
    assert node.params == ["x"]
    assert node.body == body
    assert node.return_expr is None


def test_function_declaration_with_return():
    return_expr = BinaryOp("+", Identifier("a"), Identifier("b"))
    node = FunctionDeclaration("add", ["a", "b"], [], return_expr)
    assert node.params == ["a", "b"]
    assert node.return_expr is return_expr


def test_function_declaration_no_params():
    node = FunctionDeclaration("greet", [], [], None)
    assert node.params == []


# ── Program ───────────────────────────────────────────────────────────────────

def test_program_empty():
    node = Program([])
    assert node.statements == []


def test_program_with_statements():
    stmts = [
        AssignmentStatement("x", IntegerLiteral(1)),
        PrintStatement(Identifier("x")),
    ]
    node = Program(stmts)
    assert len(node.statements) == 2
    assert isinstance(node.statements[0], AssignmentStatement)
    assert isinstance(node.statements[1], PrintStatement)


# ── Nested expressions ────────────────────────────────────────────────────────

def test_nested_binary_ops():
    # x + y * 2
    inner = BinaryOp("*", Identifier("y"), IntegerLiteral(2))
    outer = BinaryOp("+", Identifier("x"), inner)
    assert isinstance(outer.right, BinaryOp)
    assert outer.right.op == "*"