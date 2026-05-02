from sly import Parser, Lexer  # noqa
from src.lexer import LanguageLexer


# ==================== Token Stream Wrapper ====================

class TypedTokenStream:
    """
    Wraps the raw lexer token stream.
    Performs a two-pass approach:
      Pass 1 (pre-scan): collect all assignment statements to build a type map.
      Pass 2 (emit):     re-emit tokens, splitting IDENTIFIER into
                         INT_IDENTIFIER or FLOAT_IDENTIFIER based on the type map.

    This eliminates the reduce/reduce conflict in the parser without
    modifying the lexer or the grammar structure.
    """

    def __init__(self, token_iter):
        self._tokens = list(token_iter)
        self._type_map = {}   # name -> 'int' | 'float' | 'bool' | 'string'
        self._prescan()

    def _prescan(self):
        """
        Scan token list for patterns:
            IDENTIFIER ASSIGNMENT <rhs_first_token>
        and infer the variable type from the rhs first meaningful token.
        This is a lightweight heuristic — full type inference happens in parser.
        """
        i = 0
        while i < len(self._tokens) - 2:
            t0 = self._tokens[i]
            t1 = self._tokens[i + 1]
            t2 = self._tokens[i + 2]
            if t0.type == 'IDENTIFIER' and t1.type == 'ASSIGNMENT':
                name = t0.value
                # Infer from first token on rhs
                if t2.type == 'INTEGER' or t2.type == 'INTEGER_UMINUS':
                    self._type_map.setdefault(name, 'int')
                elif t2.type == 'FLOAT' or t2.type == 'FLOAT_UMINUS':
                    self._type_map.setdefault(name, 'float')
                elif t2.type == 'BOOLEAN':
                    self._type_map.setdefault(name, 'bool')
                elif t2.type == 'STRING':
                    self._type_map.setdefault(name, 'string')
                elif t2.type == 'IDENTIFIER':
                    # Propagate known type from rhs identifier
                    rhs_type = self._type_map.get(t2.value)
                    if rhs_type:
                        self._type_map.setdefault(name, rhs_type)
            i += 1

        # Second micro-pass: propagate remaining unknowns
        changed = True
        while changed:
            changed = False
            i = 0
            while i < len(self._tokens) - 2:
                t0 = self._tokens[i]
                t1 = self._tokens[i + 1]
                t2 = self._tokens[i + 2]
                if t0.type == 'IDENTIFIER' and t1.type == 'ASSIGNMENT' and t2.type == 'IDENTIFIER':
                    name = t0.value
                    rhs_type = self._type_map.get(t2.value)
                    if rhs_type and name not in self._type_map:
                        self._type_map[name] = rhs_type
                        changed = True
                i += 1

    def __iter__(self):
        for tok in self._tokens:
            if tok.type == 'IDENTIFIER':
                known_type = self._type_map.get(tok.value)
                if known_type == 'float':
                    tok.type = 'FLOAT_IDENTIFIER'
                else:
                    # int, bool, string, unknown → INT_IDENTIFIER
                    # bool/string identifiers in expression context are rare;
                    # semantic analysis handles misuse
                    tok.type = 'INT_IDENTIFIER'
            yield tok


# ==================== Parser ====================

class LanguageParser(Parser):  # noqa
    # Extend token set with the two split identifier tokens
    tokens = (LanguageLexer.tokens - {'IDENTIFIER'}) | {'INT_IDENTIFIER', 'FLOAT_IDENTIFIER'}

    precedence = (
        ('left', 'STRING_CONCAT'),  # noqa
        ('left', 'INTEGER_ADDITION', 'INTEGER_SUBTRACTION'),  # noqa
        ('left', 'INTEGER_MULTIPLICATION', 'INTEGER_DIVISION'),  # noqa
        ('left', 'FLOAT_ADDITION', 'FLOAT_SUBTRACTION'),  # noqa
        ('left', 'FLOAT_MULTIPLICATION', 'FLOAT_DIVISION'),  # noqa
        ('right', 'INTEGER_UMINUS'),  # noqa
        ('right', 'FLOAT_UMINUS'),  # noqa
    )

    def __init__(self):
        self.is_syntax_error = False

    # ==================== Program ====================

    @_('statement_list')  # noqa
    def program(self, p):
        return ('program', p.statement_list)

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

    @_('INT_IDENTIFIER ASSIGNMENT expression')  # noqa
    def assignment_statement(self, p):
        return ('assign', p.INT_IDENTIFIER, p.expression)

    @_('FLOAT_IDENTIFIER ASSIGNMENT expression')  # noqa
    def assignment_statement(self, p):
        return ('assign', p.FLOAT_IDENTIFIER, p.expression)

    # ==================== IfStatement ====================

    @_('IF PAREN_OPEN boolean_expression PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE else_clause')  # noqa
    def if_statement(self, p):
        return ('if', p.boolean_expression, p.statement_list, p.else_clause)

    # ==================== ElseClause ====================

    @_('ELSE BRACE_OPEN statement_list BRACE_CLOSE')  # noqa
    def else_clause(self, p):
        return ('else', p.statement_list)

    @_('')  # noqa
    def else_clause(self, p):
        return None

    # ==================== WhileStatement ====================

    @_('WHILE PAREN_OPEN boolean_expression PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE')  # noqa
    def while_statement(self, p):
        return ('while', p.boolean_expression, p.statement_list)

    # ==================== PrintStatement ====================

    @_('PRINT PAREN_OPEN expression PAREN_CLOSE')  # noqa
    def print_statement(self, p):
        return ('print', p.expression)

    # ==================== FunctionDeclaration ====================

    @_('FUNCTION INT_IDENTIFIER PAREN_OPEN parameter_list PAREN_CLOSE BRACE_OPEN statement_list return_statement BRACE_CLOSE')  # noqa
    def function_declaration(self, p):
        return ('function', p.INT_IDENTIFIER, p.parameter_list, p.statement_list, p.return_statement)

    # ==================== ParameterList ====================

    @_('INT_IDENTIFIER COMMA parameter_list')  # noqa
    def parameter_list(self, p):
        return [p.INT_IDENTIFIER] + p.parameter_list

    @_('INT_IDENTIFIER')  # noqa
    def parameter_list(self, p):
        return [p.INT_IDENTIFIER]

    @_('')  # noqa
    def parameter_list(self, p):
        return []

    # ==================== ReturnStatement ====================

    @_('RETURN expression')  # noqa
    def return_statement(self, p):
        return ('return', p.expression)

    @_('')  # noqa
    def return_statement(self, p):
        return None

    # ==================== BooleanExpression ====================

    @_('int_expression INTEGER_EQUALITY int_expression')  # noqa
    def boolean_expression(self, p):
        return ('int_eq', p.int_expression0, p.int_expression1)

    @_('int_expression INTEGER_INEQUALITY int_expression')  # noqa
    def boolean_expression(self, p):
        return ('int_neq', p.int_expression0, p.int_expression1)

    @_('float_expression FLOAT_EQUALITY float_expression')  # noqa
    def boolean_expression(self, p):
        return ('float_eq', p.float_expression0, p.float_expression1)

    @_('float_expression FLOAT_INEQUALITY float_expression')  # noqa
    def boolean_expression(self, p):
        return ('float_neq', p.float_expression0, p.float_expression1)

    @_('BOOLEAN')  # noqa
    def boolean_expression(self, p):
        return ('boolean', p.BOOLEAN)

    # ==================== Expression ====================

    @_('int_expression')  # noqa
    def expression(self, p):
        return p.int_expression

    @_('float_expression')  # noqa
    def expression(self, p):
        return p.float_expression

    @_('string_expression')  # noqa
    def expression(self, p):
        return p.string_expression

    @_('boolean_expression')  # noqa
    def expression(self, p):
        return p.boolean_expression

    # ==================== IntExpression ====================

    @_('int_expression INTEGER_ADDITION int_term')  # noqa
    def int_expression(self, p):
        return ('int_add', p.int_expression, p.int_term)

    @_('int_expression INTEGER_SUBTRACTION int_term')  # noqa
    def int_expression(self, p):
        return ('int_sub', p.int_expression, p.int_term)

    @_('int_term')  # noqa
    def int_expression(self, p):
        return p.int_term

    # ==================== IntTerm ====================

    @_('int_term INTEGER_MULTIPLICATION int_factor')  # noqa
    def int_term(self, p):
        return ('int_mul', p.int_term, p.int_factor)

    @_('int_term INTEGER_DIVISION int_factor')  # noqa
    def int_term(self, p):
        return ('int_div', p.int_term, p.int_factor)

    @_('int_factor')  # noqa
    def int_term(self, p):
        return p.int_factor

    # ==================== IntFactor ====================

    @_('INTEGER')  # noqa
    def int_factor(self, p):
        return ('integer', p.INTEGER)

    @_('INT_IDENTIFIER')  # noqa
    def int_factor(self, p):
        return ('identifier', p.INT_IDENTIFIER)

    @_('PAREN_OPEN int_expression PAREN_CLOSE')  # noqa
    def int_factor(self, p):
        return p.int_expression

    @_('INTEGER_UMINUS int_factor')  # noqa
    def int_factor(self, p):
        return ('int_uminus', p.int_factor)

    # ==================== FloatExpression ====================

    @_('float_expression FLOAT_ADDITION float_term')  # noqa
    def float_expression(self, p):
        return ('float_add', p.float_expression, p.float_term)

    @_('float_expression FLOAT_SUBTRACTION float_term')  # noqa
    def float_expression(self, p):
        return ('float_sub', p.float_expression, p.float_term)

    @_('float_term')  # noqa
    def float_expression(self, p):
        return p.float_term

    # ==================== FloatTerm ====================

    @_('float_term FLOAT_MULTIPLICATION float_factor')  # noqa
    def float_term(self, p):
        return ('float_mul', p.float_term, p.float_factor)

    @_('float_term FLOAT_DIVISION float_factor')  # noqa
    def float_term(self, p):
        return ('float_div', p.float_term, p.float_factor)

    @_('float_factor')  # noqa
    def float_term(self, p):
        return p.float_factor

    # ==================== FloatFactor ====================

    @_('FLOAT')  # noqa
    def float_factor(self, p):
        return ('float', p.FLOAT)

    @_('FLOAT_IDENTIFIER')  # noqa
    def float_factor(self, p):
        return ('identifier', p.FLOAT_IDENTIFIER)

    @_('PAREN_OPEN float_expression PAREN_CLOSE')  # noqa
    def float_factor(self, p):
        return p.float_expression

    @_('FLOAT_UMINUS float_factor')  # noqa
    def float_factor(self, p):
        return ('float_uminus', p.float_factor)

    # ==================== StringExpression ====================

    @_('string_expression STRING_CONCAT string_term')  # noqa
    def string_expression(self, p):
        return ('string_concat', p.string_expression, p.string_term)

    @_('string_term')  # noqa
    def string_expression(self, p):
        return p.string_term

    @_('STRING')  # noqa
    def string_term(self, p):
        return ('string', p.STRING)

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
    lexer = LanguageLexer()
    parser = LanguageParser()
    raw_tokens = lexer.tokenize(source)
    typed_stream = TypedTokenStream(raw_tokens)
    result = parser.parse(iter(typed_stream))
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
        while (true) {
            x = x + 1
        }
        print(z)
        print(s)
        function add(p, q) {
            return p + q
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