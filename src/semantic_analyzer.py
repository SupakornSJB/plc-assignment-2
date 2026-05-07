from src.ast_node.expression import (
    BinaryOp, UnaryOp, FunctionCall, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)
from src.ast_node.statement import (
    Program, AssignmentStatement, IfStatement, WhileStatement,
    PrintStatement, FunctionDeclaration,
)


class SemanticAnalyzer:
    """
    Walks the AST and enforces semantic rules.
    Current scope: Function declaration and function call checks only.
    (BooleanExpression, If, While, Print, Assignment, Expressions are
    handled by their respective team members.)

    Raises:
        NameError   – undefined variable or undefined function called
        TypeError   – wrong number of arguments (arity mismatch)
    """

    def __init__(self):
        # symbol_table maps name → {'kind': 'variable'|'function', 'params': [...]}
        self.symbol_table: dict[str, dict] = {}
        self.errors: list[str] = []

    # ── Entry point ───────────────────────────────────────────────────────────

    def analyze(self, node: Program) -> list[str]:
        """Return list of error strings (empty = OK)."""
        self.visit(node)
        return self.errors

    # ── Dispatcher ────────────────────────────────────────────────────────────

    def visit(self, node):
        match node:
            case Program():             self._visit_program(node)
            case FunctionDeclaration(): self._visit_function_declaration(node)
            case FunctionCall():        self._visit_function_call(node)
            case AssignmentStatement(): self._visit_assignment_statement(node)
            case IfStatement():         self._visit_if_statement(node)
            case WhileStatement():      self._visit_while_statement(node)
            case PrintStatement():      self._visit_print_statement(node)
            case BinaryOp():            self._visit_binary_op(node)
            case UnaryOp():             self._visit_unary_op(node)
            case Identifier():          self._visit_identifier(node)
            case IntegerLiteral() | FloatLiteral() | StringLiteral() | BooleanLiteral():
                pass  # literals have no semantic errors
            case _:
                pass  # unknown nodes are silently skipped

    # ── Program ───────────────────────────────────────────────────────────────

    def _visit_program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    # ── Function declaration ──────────────────────────────────────────────────

    def _visit_function_declaration(self, node: FunctionDeclaration):
        # Register function in symbol table
        self.symbol_table[node.name] = {
            'kind': 'function',
            'params': node.params,
        }

        # Analyse body — params are locally declared for this scope
        local_scope = set(node.params)
        saved_table = dict(self.symbol_table)

        # Temporarily add params so identifier lookups inside body don't fail
        for param in node.params:
            self.symbol_table[param] = {'kind': 'variable'}

        for stmt in node.body:
            self.visit(stmt)

        if node.return_expr is not None:
            self.visit(node.return_expr)

        # Restore symbol table (remove params, keep anything declared in body)
        self.symbol_table = saved_table
        # Re-register the function itself (it was in saved_table already)

    # ── Function call ─────────────────────────────────────────────────────────

    def _visit_function_call(self, node: FunctionCall):
        # Check function is declared
        if node.name not in self.symbol_table:
            self.errors.append(
                f"NameError: function '{node.name}' is not defined"
            )
            return

        entry = self.symbol_table[node.name]

        if entry['kind'] != 'function':
            self.errors.append(
                f"TypeError: '{node.name}' is not a function"
            )
            return

        # Arity check
        expected = len(entry['params'])
        got = len(node.args)
        if expected != got:
            self.errors.append(
                f"TypeError: '{node.name}' expects {expected} argument(s), got {got}"
            )

        # Analyse each argument expression
        for arg in node.args:
            self.visit(arg)

    # ── Assignment ────────────────────────────────────────────────────────────

    def _visit_assignment_statement(self, node: AssignmentStatement):
        self.visit(node.expr)
        # Register variable (type checking is the interpreter's job)
        self.symbol_table[node.identifier] = {'kind': 'variable'}

    # ── If / While / Print — delegate to other team members ──────────────────
    # Included here only to keep the tree walk complete so function calls
    # nested inside these constructs are still checked.

    def _visit_if_statement(self, node: IfStatement):
        self.visit(node.condition)
        for stmt in node.then_body:
            self.visit(stmt)
        if node.else_body is not None:
            for stmt in node.else_body:
                self.visit(stmt)

    def _visit_while_statement(self, node: WhileStatement):
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)

    def _visit_print_statement(self, node: PrintStatement):
        self.visit(node.expr)

    # ── Expressions ──────────────────────────────────────────────────────────

    def _visit_binary_op(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)

    def _visit_unary_op(self, node: UnaryOp):
        self.visit(node.operand)

    def _visit_identifier(self, node: Identifier):
        if node.name not in self.symbol_table:
            self.errors.append(
                f"NameError: variable '{node.name}' is not defined"
            )