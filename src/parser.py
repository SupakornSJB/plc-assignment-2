from sly import Parser

from src.lexer import LanguageLexer
from src.ast.expression import (
    BinaryOp, UnaryOp, FunctionCall, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)
from src.ast.statement import (
    Program, AssignmentStatement, IfStatement, WhileStatement,
    PrintStatement, FunctionDeclaration,
)


class LanguageParser(Parser):
    tokens = LanguageLexer.tokens

    precedence = (
        ('left',  INTEGER_EQUALITY, INTEGER_INEQUALITY, FLOAT_EQUALITY, FLOAT_INEQUALITY),
        ('left',  INTEGER_ADDITION, INTEGER_SUBTRACTION, FLOAT_ADDITION, FLOAT_SUBTRACTION, STRING_CONCAT),
        ('left',  INTEGER_MULTIPLICATION, INTEGER_DIVISION, FLOAT_MULTIPLICATION, FLOAT_DIVISION),
        ('right', INTEGER_UMINUS, FLOAT_UMINUS),
    )

    ##### Program #####

    @_('statement_list')
    def program(self, p):
        return Program(p.statement_list)

    @_('statement statement_list')
    def statement_list(self, p):
        return [p.statement] + p.statement_list

    @_('')
    def statement_list(self, p):
        return []

    ##### Statements #####

    @_('IDENTIFIER ASSIGNMENT expr')
    def statement(self, p):
        return AssignmentStatement(p.IDENTIFIER, p.expr)

    @_('PRINT PAREN_OPEN expr PAREN_CLOSE')
    def statement(self, p):
        return PrintStatement(p.expr)

    @_('IF PAREN_OPEN bool_expr PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE else_clause')
    def statement(self, p):
        return IfStatement(p.bool_expr, p.statement_list, p.else_clause)

    @_('WHILE PAREN_OPEN bool_expr PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE')
    def statement(self, p):
        return WhileStatement(p.bool_expr, p.statement_list)

    @_('FUNCTION IDENTIFIER PAREN_OPEN param_list PAREN_CLOSE BRACE_OPEN statement_list return_stmt BRACE_CLOSE')
    def statement(self, p):
        return FunctionDeclaration(p.IDENTIFIER, p.param_list, p.statement_list, p.return_stmt)

    @_('IDENTIFIER PAREN_OPEN arg_list PAREN_CLOSE')
    def statement(self, p):
        return FunctionCall(p.IDENTIFIER, p.arg_list)

    # bool_expr is structurally identical to expr; type correctness (must
    # evaluate to bool) is enforced at runtime by the interpreter.
    @_('expr')
    def bool_expr(self, p):
        return p.expr

    ##### Else / params / return #####

    @_('ELSE BRACE_OPEN statement_list BRACE_CLOSE')
    def else_clause(self, p):
        return p.statement_list

    @_('')
    def else_clause(self, p):
        return None

    @_('IDENTIFIER COMMA param_list')
    def param_list(self, p):
        return [p.IDENTIFIER] + p.param_list

    @_('IDENTIFIER')
    def param_list(self, p):
        return [p.IDENTIFIER]

    @_('')
    def param_list(self, p):
        return []

    @_('RETURN expr')
    def return_stmt(self, p):
        return p.expr

    @_('')
    def return_stmt(self, p):
        return None

    ##### Expression #####
    # Binary ops are inlined so SLY's precedence table resolves ambiguity via
    # tokens rather than non-terminals.

    @_('expr INTEGER_ADDITION expr')
    def expr(self, p):
        return BinaryOp('+', p.expr0, p.expr1)

    @_('expr INTEGER_SUBTRACTION expr')
    def expr(self, p):
        return BinaryOp('-', p.expr0, p.expr1)

    @_('expr INTEGER_MULTIPLICATION expr')
    def expr(self, p):
        return BinaryOp('*', p.expr0, p.expr1)

    @_('expr INTEGER_DIVISION expr')
    def expr(self, p):
        return BinaryOp('/', p.expr0, p.expr1)

    @_('expr FLOAT_ADDITION expr')
    def expr(self, p):
        return BinaryOp('+.', p.expr0, p.expr1)

    @_('expr FLOAT_SUBTRACTION expr')
    def expr(self, p):
        return BinaryOp('-.', p.expr0, p.expr1)

    @_('expr FLOAT_MULTIPLICATION expr')
    def expr(self, p):
        return BinaryOp('*.', p.expr0, p.expr1)

    @_('expr FLOAT_DIVISION expr')
    def expr(self, p):
        return BinaryOp('/.', p.expr0, p.expr1)

    @_('expr STRING_CONCAT expr')
    def expr(self, p):
        return BinaryOp('++', p.expr0, p.expr1)

    @_('expr INTEGER_EQUALITY expr')
    def expr(self, p):
        return BinaryOp('==', p.expr0, p.expr1)

    @_('expr INTEGER_INEQUALITY expr')
    def expr(self, p):
        return BinaryOp('!=', p.expr0, p.expr1)

    @_('expr FLOAT_EQUALITY expr')
    def expr(self, p):
        return BinaryOp('==.', p.expr0, p.expr1)

    @_('expr FLOAT_INEQUALITY expr')
    def expr(self, p):
        return BinaryOp('!=.', p.expr0, p.expr1)

    ##### Unary #####
    @_('INTEGER_UMINUS expr')
    def expr(self, p):
        return UnaryOp('--', p.expr)

    @_('FLOAT_UMINUS expr')
    def expr(self, p):
        return UnaryOp('--.', p.expr)

    # Function call must appear before plain IDENTIFIER to let SLY's default
    # shift preference handle the IDENTIFIER vs FunctionCall ambiguity.
    @_('IDENTIFIER PAREN_OPEN arg_list PAREN_CLOSE')
    def expr(self, p):
        return FunctionCall(p.IDENTIFIER, p.arg_list)

    @_('IDENTIFIER')
    def expr(self, p):
        return Identifier(p.IDENTIFIER)

    @_('INTEGER')
    def expr(self, p):
        return IntegerLiteral(p.INTEGER)

    @_('FLOAT')
    def expr(self, p):
        return FloatLiteral(p.FLOAT)

    @_('STRING')
    def expr(self, p):
        return StringLiteral(p.STRING)

    @_('BOOLEAN')
    def expr(self, p):
        return BooleanLiteral(p.BOOLEAN)

    @_('PAREN_OPEN expr PAREN_CLOSE')
    def expr(self, p):
        return p.expr

    ##### Argument list #####

    @_('expr COMMA arg_list')
    def arg_list(self, p):
        return [p.expr] + p.arg_list

    @_('expr')
    def arg_list(self, p):
        return [p.expr]

    @_('')
    def arg_list(self, p):
        return []


if __name__ == '__main__':
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

        flag = true
        if (flag) {
            x = 99
        }

        function add(a, b) {
            return a + b
        }
        result = add(4, 5)
    '''

    lexer = LanguageLexer()
    parser = LanguageParser()
    tree = parser.parse(lexer.tokenize(source))

    print("=== AST ===")
    for stmt in tree.statements:
        print(stmt)