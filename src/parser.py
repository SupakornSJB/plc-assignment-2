from sly import Parser  # noqa
from lexer import LanguageLexer


# ==================== Parser ====================

class LanguageParser(Parser):  # noqa
    # Use the lexer's token set directly — no splitting of IDENTIFIER needed.
    # Type checking is deferred entirely to semantic analysis.
    tokens = LanguageLexer.tokens

    # Precedence table — lowest to highest.
    # Comparison operators sit at the bottom so that arithmetic binds tighter.
    precedence = (
        ('left', 'INTEGER_EQUALITY', 'INTEGER_INEQUALITY'),     # noqa  ==  !=
        ('left', 'FLOAT_EQUALITY', 'FLOAT_INEQUALITY'),         # noqa  ==. !=.
        ('left', 'STRING_CONCAT'),                               # noqa  ++
        ('left', 'INTEGER_ADDITION', 'INTEGER_SUBTRACTION'),    # noqa  +  -
        ('left', 'FLOAT_ADDITION', 'FLOAT_SUBTRACTION'),        # noqa  +. -.
        ('left', 'INTEGER_MULTIPLICATION', 'INTEGER_DIVISION'), # noqa  *  /
        ('left', 'FLOAT_MULTIPLICATION', 'FLOAT_DIVISION'),     # noqa  *. /.
        ('right', 'INTEGER_UMINUS'),                             # noqa  --
        ('right', 'FLOAT_UMINUS'),                               # noqa  --.
    )

    def __init__(self):
        self.is_syntax_error = False

    # ==================== Program ====================

    @_('statement_list')  # noqa
    def program(self, p):
        return ('program', p.statement_list)  # noqa

    # ==================== StatementList ====================

    @_('statement statement_list')  # noqa
    def statement_list(self, p):
        return [p.statement] + p.statement_list

    @_('')  # noqa
    def statement_list(self, p):
        return []

    # ==================== Statement ====================

    @_('assignment_statement')  # noqa
    def statement(self, p):
        return p.assignment_statement

    @_('if_statement')  # noqa
    def statement(self, p):
        return p.if_statement

    @_('while_statement')  # noqa
    def statement(self, p):
        return p.while_statement

    @_('print_statement')  # noqa
    def statement(self, p):
        return p.print_statement

    @_('function_declaration')  # noqa
    def statement(self, p):
        return p.function_declaration

    # ==================== AssignmentStatement ====================
    # AssignmentStatement → IDENTIFIER "=" Expression

    @_('IDENTIFIER ASSIGNMENT expression')  # noqa
    def assignment_statement(self, p):
        return ('assign', p.IDENTIFIER, p.expression)  # noqa

    # ==================== IfStatement ====================
    # IfStatement → "if" "(" BooleanExpression ")" "{" StatementList "}" ElseClause

    @_('IF PAREN_OPEN boolean_expression PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE else_clause')  # noqa
    def if_statement(self, p):
        return ('if', p.boolean_expression, p.statement_list, p.else_clause)  # noqa

    # ==================== ElseClause ====================
    # ElseClause → "else" "{" StatementList "}" | ε

    @_('ELSE BRACE_OPEN statement_list BRACE_CLOSE')  # noqa
    def else_clause(self, p):
        return ('else', p.statement_list)  # noqa

    @_('')  # noqa
    def else_clause(self, p):
        return None

    # ==================== WhileStatement ====================
    # WhileStatement → "while" "(" BooleanExpression ")" "{" StatementList "}"

    @_('WHILE PAREN_OPEN boolean_expression PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE')  # noqa
    def while_statement(self, p):
        return ('while', p.boolean_expression, p.statement_list)  # noqa

    # ==================== PrintStatement ====================
    # PrintStatement → "print" "(" Expression ")"

    @_('PRINT PAREN_OPEN expression PAREN_CLOSE')  # noqa
    def print_statement(self, p):
        return ('print', p.expression)  # noqa

    # ==================== FunctionDeclaration ====================
    # FunctionDeclaration → "function" IDENTIFIER "(" ParameterList ")" "{" StatementList ReturnStatement "}"

    @_('FUNCTION IDENTIFIER PAREN_OPEN parameter_list PAREN_CLOSE BRACE_OPEN statement_list return_statement BRACE_CLOSE')  # noqa
    def function_declaration(self, p):
        return ('function', p.IDENTIFIER, p.parameter_list, p.statement_list, p.return_statement)  # noqa

    # ==================== ParameterList ====================
    # ParameterList → IDENTIFIER "," ParameterList | IDENTIFIER | ε

    @_('IDENTIFIER COMMA parameter_list')  # noqa
    def parameter_list(self, p):
        return [p.IDENTIFIER] + p.parameter_list

    @_('IDENTIFIER')  # noqa
    def parameter_list(self, p):
        return [p.IDENTIFIER]

    @_('')  # noqa
    def parameter_list(self, p):
        return []

    # ==================== ReturnStatement ====================
    # ReturnStatement → "return" Expression | ε

    @_('RETURN expression')  # noqa
    def return_statement(self, p):
        return ('return', p.expression)  # noqa

    @_('')  # noqa
    def return_statement(self, p):
        return None

    # ==================== BooleanExpression ====================
    # Used exclusively as the condition in if/while.
    # Duplicating the four comparison rules from Expression is intentional —
    # see grammar note: adding Expression → BooleanExpression creates a circular
    # dependency that causes hundreds of LALR(1) conflicts.
    # Type correctness of operands is enforced in semantic analysis.
    #
    # BooleanExpression → Expression "==" Expression
    #                   | Expression "!=" Expression
    #                   | Expression "==." Expression
    #                   | Expression "!=." Expression
    #                   | IDENTIFIER
    #                   | BOOLEAN

    @_('expression INTEGER_EQUALITY expression')  # noqa
    def boolean_expression(self, p):
        return ('int_eq', p.expression0, p.expression1)  # noqa

    @_('expression INTEGER_INEQUALITY expression')  # noqa
    def boolean_expression(self, p):
        return ('int_neq', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_EQUALITY expression')  # noqa
    def boolean_expression(self, p):
        return ('float_eq', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_INEQUALITY expression')  # noqa
    def boolean_expression(self, p):
        return ('float_neq', p.expression0, p.expression1)  # noqa

    @_('IDENTIFIER')  # noqa
    def boolean_expression(self, p):
        return ('identifier', p.IDENTIFIER)  # noqa

    @_('BOOLEAN')  # noqa
    def boolean_expression(self, p):
        return ('boolean', p.BOOLEAN)  # noqa

    # ==================== Expression ====================
    # Unified expression — no int/float/string split.
    # All operator rules mirror the grammar exactly.
    # Type correctness is enforced in semantic analysis.

    # --- Comparison (also appear in BooleanExpression for if/while conditions) ---
    @_('expression INTEGER_EQUALITY expression')  # noqa
    def expression(self, p):
        return ('int_eq', p.expression0, p.expression1)  # noqa

    @_('expression INTEGER_INEQUALITY expression')  # noqa
    def expression(self, p):
        return ('int_neq', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_EQUALITY expression')  # noqa
    def expression(self, p):
        return ('float_eq', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_INEQUALITY expression')  # noqa
    def expression(self, p):
        return ('float_neq', p.expression0, p.expression1)  # noqa

    # --- Integer arithmetic ---
    @_('expression INTEGER_ADDITION expression')  # noqa
    def expression(self, p):
        return ('int_add', p.expression0, p.expression1)  # noqa

    @_('expression INTEGER_SUBTRACTION expression')  # noqa
    def expression(self, p):
        return ('int_sub', p.expression0, p.expression1)  # noqa

    @_('expression INTEGER_MULTIPLICATION expression')  # noqa
    def expression(self, p):
        return ('int_mul', p.expression0, p.expression1)  # noqa

    @_('expression INTEGER_DIVISION expression')  # noqa
    def expression(self, p):
        return ('int_div', p.expression0, p.expression1)  # noqa

    # --- Float arithmetic ---
    @_('expression FLOAT_ADDITION expression')  # noqa
    def expression(self, p):
        return ('float_add', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_SUBTRACTION expression')  # noqa
    def expression(self, p):
        return ('float_sub', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_MULTIPLICATION expression')  # noqa
    def expression(self, p):
        return ('float_mul', p.expression0, p.expression1)  # noqa

    @_('expression FLOAT_DIVISION expression')  # noqa
    def expression(self, p):
        return ('float_div', p.expression0, p.expression1)  # noqa

    # --- String concatenation ---
    @_('expression STRING_CONCAT expression')  # noqa
    def expression(self, p):
        return ('string_concat', p.expression0, p.expression1)  # noqa

    # --- Unary minus ---
    @_('INTEGER_UMINUS expression')  # noqa
    def expression(self, p):
        return ('int_uminus', p.expression)  # noqa

    @_('FLOAT_UMINUS expression')  # noqa
    def expression(self, p):
        return ('float_uminus', p.expression)  # noqa

    # --- Parenthesised expression ---
    @_('PAREN_OPEN expression PAREN_CLOSE')  # noqa
    def expression(self, p):
        return p.expression

    # --- Function call (must come before plain IDENTIFIER to avoid ambiguity) ---
    @_('function_call')  # noqa
    def expression(self, p):
        return p.function_call

    # --- Identifier ---
    @_('IDENTIFIER')  # noqa
    def expression(self, p):
        return ('identifier', p.IDENTIFIER)  # noqa

    # --- Literals ---
    @_('INTEGER')  # noqa
    def expression(self, p):
        return ('integer', p.INTEGER)  # noqa

    @_('FLOAT')  # noqa
    def expression(self, p):
        return ('float', p.FLOAT)  # noqa

    @_('STRING')  # noqa
    def expression(self, p):
        return ('string', p.STRING)  # noqa

    @_('BOOLEAN')  # noqa
    def expression(self, p):
        return ('boolean', p.BOOLEAN)  # noqa

    # ==================== FunctionCall ====================
    # FunctionCall → IDENTIFIER "(" ArgumentList ")"

    @_('IDENTIFIER PAREN_OPEN argument_list PAREN_CLOSE')  # noqa
    def function_call(self, p):
        return ('call', p.IDENTIFIER, p.argument_list)  # noqa

    # ==================== ArgumentList ====================
    # ArgumentList → Expression "," ArgumentList | Expression | ε

    @_('expression COMMA argument_list')  # noqa
    def argument_list(self, p):
        return [p.expression] + p.argument_list

    @_('expression')  # noqa
    def argument_list(self, p):
        return [p.expression]

    @_('')  # noqa
    def argument_list(self, p):
        return []

    # ==================== Error Handling ====================

    def error(self, p):
        self.is_syntax_error = True
        if p:
            print(f"ERROR: Syntax error at token '{p.value}' (type: {p.type}) at line {p.lineno}")
        else:
            print("ERROR: Syntax error at end of input")


# ==================== Public parse function ====================

def parse_program(source: str):
    """
    Tokenize *source* and parse it.
    Returns (result, lexer, parser).
    """
    lexer = LanguageLexer()   # noqa
    parser = LanguageParser() # noqa
    tokens = lexer.tokenize(source)
    result = parser.parse(tokens)  # noqa
    return result, lexer, parser


# ==================== Test ====================

if __name__ == '__main__':
    test_input = '''
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
        if (x == y) {
            x = 0
        } else {
            x = 1
        }
        if (a ==. b) {
            a = 0.0
        }
        if (x != y) {
            x = 99
        }
        if (a !=. b) {
            a = 99.0
        }
        while (flag) {
            x = x + 1
        }
        while (true) {
            x = x + 1
        }
        print(z)
        print(s)
        function add(p, q) {
            return p + q
        }
        r = add(x, y)
        print(r)
        print(add(1, 2))
        function greet() {
            return 'hello'
        }
    '''

    result, lexer, parser = parse_program(test_input)

    if not lexer.is_lexical_error and not parser.is_syntax_error:
        print("=" * 50)
        print("PARSING SUCCESSFUL!")
        print("=" * 50)
        print("\nAbstract Syntax Tree (AST):")

        import json

        def ast_to_dict(node):
            if isinstance(node, tuple):
                return {node[0]: [ast_to_dict(child) for child in node[1:]]}
            elif isinstance(node, list):
                return [ast_to_dict(item) for item in node]
            else:
                return node

        print(json.dumps(ast_to_dict(result), indent=2))
    else:
        print("=" * 50)
        print("PARSING FAILED!")
        print("=" * 50)