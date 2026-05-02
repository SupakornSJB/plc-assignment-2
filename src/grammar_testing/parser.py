from sly import Lexer, Parser

# ----------------- LEXER -----------------

class MyLexer(Lexer):
    tokens = {
        IDENTIFIER, INTEGER, FLOAT, STRING, BOOLEAN,
        PLUS, MINUS, TIMES, DIVIDE,
        FPLUS, FMINUS, FTIMES, FDIVIDE,
        UMINUS, FUMINUS,
        EQ, NEQ, FEQ, FNEQ,
        CONCAT,
        ASSIGN,
        IF, ELSE, WHILE, PRINT, FUNCTION, RETURN
    }

    literals = { '(', ')', '{', '}', ',', }

    # Operators — longer patterns must come before their prefixes
    FPLUS   = r'\+\.'
    FUMINUS = r'--\.'   # must come before FMINUS
    FMINUS  = r'-\.'
    FTIMES  = r'\*\.'
    FDIVIDE = r'/\.'
    CONCAT  = r'\+\+'
    FEQ     = r'==\.'
    FNEQ    = r'!=\.'

    PLUS   = r'\+'
    UMINUS = r'--'      # must come before MINUS
    MINUS  = r'-'
    TIMES  = r'\*'
    DIVIDE = r'/'
    EQ     = r'=='
    NEQ    = r'!='
    ASSIGN = r'='

    # Identifiers & keywords
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENTIFIER['if']       = IF
    IDENTIFIER['else']     = ELSE
    IDENTIFIER['while']    = WHILE
    IDENTIFIER['print']    = PRINT
    IDENTIFIER['function'] = FUNCTION
    IDENTIFIER['return']   = RETURN
    IDENTIFIER['true']     = BOOLEAN
    IDENTIFIER['false']    = BOOLEAN

    FLOAT   = r'\d+\.\d+'
    INTEGER = r'\d+'
    STRING  = r'\".*?\"'

    ignore = ' \t\n'


# ----------------- PARSER -----------------

class MyParser(Parser):
    debugfile = 'parser.out'
    tokens = MyLexer.tokens

    # Precedence (low → high)
    precedence = (
        ('left',  EQ, NEQ, FEQ, FNEQ),
        ('left',  PLUS, MINUS, FPLUS, FMINUS, CONCAT),
        ('left',  TIMES, DIVIDE, FTIMES, FDIVIDE),
        ('right', UMINUS, FUMINUS),
    )

    # Program
    @_('statement_list')
    def program(self, p):
        return p.statement_list

    @_('expr')
    def program(self, p):
        return p.expr

    @_('statement statement_list')
    def statement_list(self, p):
        return [p.statement] + p.statement_list

    @_('')
    def statement_list(self, p):
        return []

    # Statements
    @_('IDENTIFIER ASSIGN expr')
    def statement(self, p):
        return ('assign', p.IDENTIFIER, p.expr)

    @_('PRINT "(" expr ")"')
    def statement(self, p):
        return ('print', p.expr)

    @_('IF "(" bool_expr ")" "{" statement_list "}" else_clause')
    def statement(self, p):
        return ('if', p.bool_expr, p.statement_list, p.else_clause)

    @_('WHILE "(" bool_expr ")" "{" statement_list "}"')
    def statement(self, p):
        return ('while', p.bool_expr, p.statement_list)

    @_('FUNCTION IDENTIFIER "(" param_list ")" "{" statement_list return_stmt "}"')
    def statement(self, p):
        return ('func', p.IDENTIFIER, p.param_list, p.statement_list, p.return_stmt)

    # bool_expr — any expression is a valid condition; type checking is left
    # to the semantic analysis phase.
    @_('expr')
    def bool_expr(self, p):
        return p.expr

    # Else / params / return
    @_('ELSE "{" statement_list "}"')
    def else_clause(self, p):
        return p.statement_list

    @_('')
    def else_clause(self, p):
        return None

    @_('IDENTIFIER "," param_list')
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

    # Expressions — binary operators inlined so SLY's precedence table can
    # anchor to tokens directly (non-terminal operators block this mechanism).
    @_('expr PLUS expr')
    def expr(self, p):
        return ('+', p.expr0, p.expr1)

    @_('expr MINUS expr')
    def expr(self, p):
        return ('-', p.expr0, p.expr1)

    @_('expr TIMES expr')
    def expr(self, p):
        return ('*', p.expr0, p.expr1)

    @_('expr DIVIDE expr')
    def expr(self, p):
        return ('/', p.expr0, p.expr1)

    @_('expr FPLUS expr')
    def expr(self, p):
        return ('+.', p.expr0, p.expr1)

    @_('expr FMINUS expr')
    def expr(self, p):
        return ('-.', p.expr0, p.expr1)

    @_('expr FTIMES expr')
    def expr(self, p):
        return ('*.', p.expr0, p.expr1)

    @_('expr FDIVIDE expr')
    def expr(self, p):
        return ('/.', p.expr0, p.expr1)

    @_('expr CONCAT expr')
    def expr(self, p):
        return ('++', p.expr0, p.expr1)

    @_('expr EQ expr')
    def expr(self, p):
        return ('==', p.expr0, p.expr1)

    @_('expr NEQ expr')
    def expr(self, p):
        return ('!=', p.expr0, p.expr1)

    @_('expr FEQ expr')
    def expr(self, p):
        return ('==.', p.expr0, p.expr1)

    @_('expr FNEQ expr')
    def expr(self, p):
        return ('!=.', p.expr0, p.expr1)

    # Unary — dedicated tokens (no %prec needed since there is no overloading)
    @_('UMINUS expr')
    def expr(self, p):
        return ('neg', p.expr)

    @_('FUMINUS expr')
    def expr(self, p):
        return ('fneg', p.expr)

    # Function call — folded directly into expr to avoid the IDENTIFIER vs
    # FunctionCall shift-reduce conflict (LALR default shift handles it correctly
    # but the separate non-terminal would still produce a warning).
    @_('IDENTIFIER "(" arg_list ")"')
    def expr(self, p):
        return ('call', p.IDENTIFIER, p.arg_list)

    @_('IDENTIFIER')
    def expr(self, p):
        return ('var', p.IDENTIFIER)

    @_('INTEGER')
    def expr(self, p):
        return ('int', p.INTEGER)

    @_('FLOAT')
    def expr(self, p):
        return ('float', p.FLOAT)

    @_('STRING')
    def expr(self, p):
        return ('string', p.STRING)

    @_('BOOLEAN')
    def expr(self, p):
        return ('bool', p.BOOLEAN)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    # arg_list
    @_('expr "," arg_list')
    def arg_list(self, p):
        return [p.expr] + p.arg_list

    @_('expr')
    def arg_list(self, p):
        return [p.expr]

    @_('')
    def arg_list(self, p):
        return []