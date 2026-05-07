from abc import ABC

from src.ast.expression import ASTNode, Expression


class Statement(ASTNode, ABC):
    pass


# ── Program ───────────────────────────────────────────────────────────────────

class Program(ASTNode):
    def __init__(self, statements: list) -> None:
        self.statements = statements

    def __repr__(self) -> str:
        return f"Program({self.statements!r})"


# ── Statements ────────────────────────────────────────────────────────────────

class AssignmentStatement(Statement):
    def __init__(self, identifier: str, expr: Expression) -> None:
        self.identifier = identifier
        self.expr = expr

    def __repr__(self) -> str:
        return f"Assign({self.identifier!r}, {self.expr!r})"


class IfStatement(Statement):
    def __init__(self, condition: Expression, then_body: list, else_body) -> None:
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body  # list[Statement] or None

    def __repr__(self) -> str:
        return f"If({self.condition!r}, {self.then_body!r}, {self.else_body!r})"


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: list) -> None:
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"While({self.condition!r}, {self.body!r})"


class PrintStatement(Statement):
    def __init__(self, expr: Expression) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return f"Print({self.expr!r})"


class FunctionDeclaration(Statement):
    def __init__(self, name: str, params: list, body: list, return_expr) -> None:
        self.name = name
        self.params = params        # list[str]
        self.body = body            # list[Statement]
        self.return_expr = return_expr  # Expression or None

    def __repr__(self) -> str:
        return f"FuncDecl({self.name!r}, {self.params!r}, {self.body!r}, {self.return_expr!r})"