from src.ast_node.expression import (
    BinaryOp, UnaryOp, FunctionCall, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)
from src.ast_node.statement import (
    Program, AssignmentStatement, IfStatement, WhileStatement,
    PrintStatement, FunctionDeclaration,
)
from src.memory import Memory


class Interpreter:

    def __init__(self):
        self.memory = Memory()
        self.int_operators = ['+', '-', '*', '/', '==', '!=']
        self.float_operators = ['+.', '-.', '*.', '/.', '==.', '!=.']
        self.string_operators = ['++']

    def visit(self, node):
        match node:
            case Program():                self.visit_program(node)
            case AssignmentStatement():    self.visit_assignment_statement(node)
            case IfStatement():            self.visit_if_statement(node)
            case WhileStatement():         self.visit_while_statement(node)
            case PrintStatement():         self.visit_print_statement(node)
            case FunctionDeclaration():    self.visit_function_declaration(node)
            case FunctionCall():           return self.visit_function_call(node)
            case BinaryOp():               return self.visit_binary_op(node)
            case UnaryOp():                return self.visit_unary_op(node)
            case Identifier():             return self.visit_identifier(node)
            case IntegerLiteral():         return self.visit_integer_literal(node)
            case FloatLiteral():           return self.visit_float_literal(node)
            case StringLiteral():          return self.visit_string_literal(node)
            case BooleanLiteral():         return self.visit_boolean_literal(node)
            case _:
                raise NotImplementedError(f"No visitor implemented for {type(node).__name__}")
        return None

    def visit_program(self, node: Program) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_assignment_statement(self, node: AssignmentStatement) -> None:
        value = self.visit(node.expr)
        self.memory.set(node.identifier, value, self._type_of(value))

    def visit_if_statement(self, node: IfStatement) -> None:
        cond = self.visit(node.condition)
        self._require_bool(cond, 'if')
        if cond:
            self.memory.push_scope()
            for stmt in node.then_body:
                self.visit(stmt)
            self.memory.pop_scope()
        elif node.else_body is not None:
            self.memory.push_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.memory.pop_scope()

    def visit_while_statement(self, node: WhileStatement) -> None:
        while True:
            cond = self.visit(node.condition)
            self._require_bool(cond, 'while')
            if not cond:
                break
            self.memory.push_scope()
            for statement in node.body:
                self.visit(statement)
            self.memory.pop_scope()

    def visit_print_statement(self, node: PrintStatement) -> None:
        print(self.visit(node.expr))

    def visit_function_declaration(self, node: FunctionDeclaration) -> None:
        self.memory.set(node.name, node, 'function')

    def visit_function_call(self, node: FunctionCall):
        entry = self.memory.get(node.name)
        func = entry['value']
        if not isinstance(func, FunctionDeclaration):
            raise TypeError(f"'{node.name}' is not a function")

        # Evaluate arguments in the CURRENT (caller) scope before pushing
        args = [self.visit(a) for a in node.args]

        if len(args) != len(func.params):
            raise TypeError(
                f"'{node.name}' expects {len(func.params)} argument(s), got {len(args)}"
            )

        # Push a FRESH scope that only contains the parameters.
        # This ensures params shadow any outer variable with the same name,
        # and assignments inside the function body do not leak to outer scopes.
        self.memory.push_scope()
        for param, val in zip(func.params, args):
            # Inject directly into the new scope — bypasses set()'s scope-walk
            # so params are always local regardless of outer variables.
            self.memory._current[param] = {
                "value": val,
                "data_type": self._type_of(val),
            }

        for statement in func.body:
            self.visit(statement)

        result = self.visit(func.return_expr) if func.return_expr is not None else None
        self.memory.pop_scope()
        return result

    def visit_binary_op(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.op in self.int_operators:
            self._require_int(left, 'binary_op')
            self._require_int(right, 'binary_op')
        elif node.op in self.float_operators:
            self._require_float(left, 'binary_op')
            self._require_float(right, 'binary_op')
        elif node.op in self.string_operators:
            self._require_string(left, 'binary_op')
            self._require_string(right, 'binary_op')
        else:
            raise NotImplementedError(f"Unknown operator {node.op!r}")

        match node.op:
            case '+':    return left + right
            case '-':    return left - right
            case '*':    return left * right
            case '/':    return left // right
            case '+.':   return left + right
            case '-.':   return left - right
            case '*.':   return left * right
            case '/.':   return left / right
            case '++':   return left + right
            case '==':   return left == right
            case '!=':   return left != right
            case '==.':  return left == right
            case '!=.':  return left != right
            case _: raise NotImplementedError(f"Unknown operator {node.op!r}")

    def visit_unary_op(self, node: UnaryOp):
        operand = self.visit(node.operand)
        if node.op == '--':
            self._require_int(operand, 'unary_op')
        elif node.op == '--.':
            self._require_float(operand, 'unary_op')
        else:
            raise NotImplementedError(f"Unknown operator {node.op!r}")

        match node.op:
            case '--':   return -operand
            case '--.':  return -operand
            case _: raise NotImplementedError(f"Unknown unary operator {node.op!r}")

    def visit_identifier(self, node: Identifier):
        return self.memory.get(node.name)['value']

    @staticmethod
    def visit_integer_literal(node: IntegerLiteral):
        return node.value

    @staticmethod
    def visit_float_literal(node: FloatLiteral):
        return node.value

    @staticmethod
    def visit_string_literal(node: StringLiteral):
        return node.value

    @staticmethod
    def visit_boolean_literal(node: BooleanLiteral):
        return node.value

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _type_of(value) -> str:
        # bool must be checked before int because bool is a subclass of int
        if isinstance(value, bool):  return 'bool'
        if isinstance(value, int):   return 'int'
        if isinstance(value, float): return 'float'
        if isinstance(value, str):   return 'string'
        return 'unknown'

    @staticmethod
    def _require_bool(value, context: str):
        if not isinstance(value, bool):
            raise TypeError(
                f"{context} condition must evaluate to bool, got {type(value).__name__}"
            )

    @staticmethod
    def _require_int(value, context: str):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"{context} requires int, got {type(value).__name__}"
            )

    @staticmethod
    def _require_float(value, context: str):
        if not isinstance(value, float):
            raise TypeError(
                f"{context} requires float, got {type(value).__name__}"
            )

    @staticmethod
    def _require_string(value, context: str):
        if not isinstance(value, str):
            raise TypeError(
                f"{context} requires string, got {type(value).__name__}"
            )


if __name__ == '__main__':
    from src.lexer import LanguageLexer
    from src.parser import LanguageParser

    source = '''
        x = 10
        y = 3

        if (x != y) {
            print(x)
        } else {
            print(y)
        }

        i = 0
        while (i != 3) {
            i = i + 1
        }
        print(i)

        flag = true
        if (flag) {
            x = 99
        }
        print(x)

        function add(a, b) {
            return a + b
        }
        result = add(4, 5)
        print(result)
    '''

    lexer = LanguageLexer()
    parser = LanguageParser()
    tree = parser.parse(lexer.tokenize(source))

    interpreter = Interpreter()
    print("=== Output ===")
    interpreter.visit(tree)
    print("\n=== Memory ===")
    print(interpreter.memory)