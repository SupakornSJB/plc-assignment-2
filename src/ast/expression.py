from abc import ABC


class ASTNode(ABC):
    pass


class Expression(ASTNode, ABC):
    pass


# ── Operators ─────────────────────────────────────────────────────────────────

class BinaryOp(Expression):
    """op values: +  -  *  /  +.  -.  *.  /.  ++  ==  !=  ==.  !=."""
    def __init__(self, op: str, left: Expression, right: Expression) -> None:
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOp({self.op!r}, {self.left!r}, {self.right!r})"


class UnaryOp(Expression):
    """op values: -- (integer negation)  --. (float negation)"""
    def __init__(self, op: str, operand: Expression) -> None:
        self.op = op
        self.operand = operand

    def __repr__(self) -> str:
        return f"UnaryOp({self.op!r}, {self.operand!r})"


# ── Calls & identifiers ───────────────────────────────────────────────────────

class FunctionCall(Expression):
    def __init__(self, name: str, args: list) -> None:
        self.name = name
        self.args = args  # list[Expression]

    def __repr__(self) -> str:
        return f"Call({self.name!r}, {self.args!r})"


class Identifier(Expression):
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Var({self.name!r})"


# ── Literals ──────────────────────────────────────────────────────────────────

class IntegerLiteral(Expression):
    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Int({self.value!r})"


class FloatLiteral(Expression):
    def __init__(self, value: float) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Float({self.value!r})"


class StringLiteral(Expression):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Str({self.value!r})"


class BooleanLiteral(Expression):
    def __init__(self, value: bool) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Bool({self.value!r})"