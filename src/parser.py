from sly import Parser
from lexer import LanguageLexer  # Import lexer của bạn


class LanguageParser(Parser):
    tokens = LanguageLexer.tokens

    # Define precedence##############
    precedence = (
        ('left', INTEGER_ADDITION, INTEGER_SUBTRACTION),
        ('left', INTEGER_MULTIPLICATION, INTEGER_DIVISION),
        ('left', FLOAT_ADDITION, FLOAT_SUBTRACTION),
        ('left', FLOAT_MULTIPLICATION, FLOAT_DIVISION),
        ('right', INTEGER_UMINUS),
        ('right', FLOAT_UMINUS),
        #('left', STRING_CONCAT),
    )

    def __init__(self):
        self.is_syntax_error = False

    #  Program

    @_('statement_list')
    def program(self, p):
        return ('program', p.statement_list)

    #  StatementList

    @_('statement statement_list')
    def statement_list(self, p):
        return [p.statement] + p.statement_list

    @_('')
    def statement_list(self, p):
        return []

    #  Statement

    @_('assignment_statement')
    def statement(self, p):
        return p.assignment_statement

    @_('if_statement')
    def statement(self, p):
        return p.if_statement

    @_('while_statement')
    def statement(self, p):
        return p.while_statement

    @_('print_statement')
    def statement(self, p):
        return p.print_statement

    @_('function_declaration')
    def statement(self, p):
        return p.function_declaration

    #  AssignmentStatement

    @_('IDENTIFIER ASSIGNMENT expression')
    def assignment_statement(self, p):
        return ('assign', p.IDENTIFIER, p.expression)

    # IfStatement

    @_('IF PAREN_OPEN boolean_expression PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE else_clause')
    def if_statement(self, p):
        return ('if', p.boolean_expression, p.statement_list, p.else_clause)

    #  ElseClause

    @_('ELSE BRACE_OPEN statement_list BRACE_CLOSE')
    def else_clause(self, p):
        return ('else', p.statement_list)

    @_('')
    def else_clause(self, p):
        return None

    #  WhileStatement

    @_('WHILE PAREN_OPEN boolean_expression PAREN_CLOSE BRACE_OPEN statement_list BRACE_CLOSE')
    def while_statement(self, p):
        return ('while', p.boolean_expression, p.statement_list)

    #PrintStatement

    @_('PRINT PAREN_OPEN expression PAREN_CLOSE')
    def print_statement(self, p):
        return ('print', p.expression)

    # FunctionDeclaration

    @_('FUNCTION IDENTIFIER PAREN_OPEN parameter_list PAREN_CLOSE BRACE_OPEN statement_list return_statement BRACE_CLOSE')
    def function_declaration(self, p):
        return ('function', p.IDENTIFIER, p.parameter_list, p.statement_list, p.return_statement)

    # ParameterList

    @_('IDENTIFIER COMMA parameter_list')
    def parameter_list(self, p):
        return [p.IDENTIFIER] + p.parameter_list

    @_('IDENTIFIER')
    def parameter_list(self, p):
        return [p.IDENTIFIER]

    @_('')
    def parameter_list(self, p):
        return []

    #  ReturnStatement

    @_('RETURN expression')
    def return_statement(self, p):
        return ('return', p.expression)

    @_('')
    def return_statement(self, p):
        return None

    #  BooleanExpression

    @_('int_expression INTEGER_EQUALITY int_expression')
    def boolean_expression(self, p):
        return ('int_eq', p.int_expression0, p.int_expression1)

    @_('int_expression INTEGER_INEQUALITY int_expression')
    def boolean_expression(self, p):
        return ('int_neq', p.int_expression0, p.int_expression1)

    @_('float_expression FLOAT_EQUALITY float_expression')
    def boolean_expression(self, p):
        return ('float_eq', p.float_expression0, p.float_expression1)

    @_('float_expression FLOAT_INEQUALITY float_expression')
    def boolean_expression(self, p):
        return ('float_neq', p.float_expression0, p.float_expression1)

    @_('BOOLEAN')
    def boolean_expression(self, p):
        return ('boolean', p.BOOLEAN)



    # Expression

    @_('int_expression')
    def expression(self, p):
        return p.int_expression

    @_('float_expression')
    def expression(self, p):
        return p.float_expression

    @_('string_expression')
    def expression(self, p):
        return p.string_expression

    @_('boolean_expression')
    def expression(self, p):
        return p.boolean_expression

    @_('PAREN_OPEN expression PAREN_CLOSE')
    def expression(self, p):
        return p.expression

    #  IntExpression

    @_('int_expression INTEGER_ADDITION int_term')
    def int_expression(self, p):
        return ('int_add', p.int_expression, p.int_term)

    @_('int_expression INTEGER_SUBTRACTION int_term')
    def int_expression(self, p):
        return ('int_sub', p.int_expression, p.int_term)

    @_('int_term')
    def int_expression(self, p):
        return p.int_term

    #  IntTerm

    @_('int_term INTEGER_MULTIPLICATION int_factor')
    def int_term(self, p):
        return ('int_mul', p.int_term, p.int_factor)

    @_('int_term INTEGER_DIVISION int_factor')
    def int_term(self, p):
        return ('int_div', p.int_term, p.int_factor)

    @_('int_factor')
    def int_term(self, p):
        return p.int_factor

    #  IntFactor

    @_('INTEGER')
    def int_factor(self, p):
        return ('integer', p.INTEGER)

    @_('IDENTIFIER')
    def int_factor(self, p):
        return ('identifier', p.IDENTIFIER)

    @_('PAREN_OPEN int_expression PAREN_CLOSE')
    def int_factor(self, p):
        return p.int_expression

    @_('INTEGER_UMINUS int_factor')
    def int_factor(self, p):
        return ('int_uminus', p.int_factor)

    #  FloatExpression

    @_('float_expression FLOAT_ADDITION float_term')
    def float_expression(self, p):
        return ('float_add', p.float_expression, p.float_term)

    @_('float_expression FLOAT_SUBTRACTION float_term')
    def float_expression(self, p):
        return ('float_sub', p.float_expression, p.float_term)

    @_('float_term')
    def float_expression(self, p):
        return p.float_term

    #  FloatTerm

    @_('float_term FLOAT_MULTIPLICATION float_factor')
    def float_term(self, p):
        return ('float_mul', p.float_term, p.float_factor)

    @_('float_term FLOAT_DIVISION float_factor')
    def float_term(self, p):
        return ('float_div', p.float_term, p.float_factor)

    @_('float_factor')
    def float_term(self, p):
        return p.float_factor

    @_('FLOAT_UMINUS float_term')
    def float_term(self, p):
        return ('float_uminus', p.float_term)

    # ==================== FloatFactor ====================

    @_('FLOAT')
    def float_factor(self, p):
        return ('float', p.FLOAT)

    @_('IDENTIFIER')
    def float_factor(self, p):
        return ('identifier', p.IDENTIFIER)

    @_('PAREN_OPEN float_expression PAREN_CLOSE')
    def float_factor(self, p):
        return p.float_expression

    # ==================== StringExpression ====================

    @_('string_expression STRING_CONCAT string_term')
    def string_expression(self, p):
        return ('string_concat', p.string_expression, p.string_term)

    @_('string_term')
    def string_expression(self, p):
        return p.string_term

    @_('STRING')
    def string_term(self, p):
        return ('string', p.STRING)

    # ==================== Error Handling ====================

    def error(self, p):
        self.is_syntax_error = True
        if p:
            print(f"ERROR: Syntax error at token '{p.value}' (type: {p.type}) at line {p.lineno}")
        else:
            print("ERROR: Syntax error at end of input")


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

    lexer = LanguageLexer()
    parser = LanguageParser()

    # Parse
    result = parser.parse(lexer.tokenize(test_input))

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
