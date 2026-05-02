from sly import Lexer, Parser

# ----------------- LEXER -----------------

class MyLexer(Lexer):
    debugfile = 'debug.log'
    tokens = {
        IDENTIFIER, INTEGER, FLOAT, STRING, BOOLEAN,
        PLUS, MINUS, TIMES, DIVIDE,
        FPLUS, FMINUS, FTIMES, FDIVIDE,
        EQ, NEQ, FEQ, FNEQ,
        CONCAT,
        ASSIGN,
        IF, ELSE, WHILE, PRINT, FUNCTION, RETURN
    }

    literals = { '(', ')', '{', '}', ',', }

    # Operators — longer patterns must come before their prefixes
    FPLUS   = r'\+\.'
    FMINUS  = r'-\.'
    FTIMES  = r'\*\.'
    FDIVIDE = r'/\.'
    CONCAT  = r'\+\+'
    FEQ     = r'==\.'
    FNEQ    = r'!=\.'

    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    EQ      = r'=='
    NEQ     = r'!='
    ASSIGN  = r'='

    # Identifiers & keywords
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENTIFIER['if'] = IF
    IDENTIFIER['else'] = ELSE
    IDENTIFIER['while'] = WHILE
    IDENTIFIER['print'] = PRINT
    IDENTIFIER['function'] = FUNCTION
    IDENTIFIER['return'] = RETURN
    IDENTIFIER['true'] = BOOLEAN
    IDENTIFIER['false'] = BOOLEAN

    FLOAT   = r'\d+\.\d+'
    INTEGER = r'\d+'
    STRING  = r'\".*?\"'

    ignore = ' \t\n'


# ----------------- PARSER -----------------

class MyParser(Parser):
    tokens = MyLexer.tokens

    # Precedence (low → high)
    precedence = (
        ('left', EQ, NEQ, FEQ, FNEQ),
        ('left', PLUS, MINUS, FPLUS, FMINUS, CONCAT),
        ('left', TIMES, DIVIDE, FTIMES, FDIVIDE),
        ('right', UMINUS),
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

    @_('IF "(" expr ")" "{" statement_list "}" else_clause')
    def statement(self, p):
        return ('if', p.expr, p.statement_list, p.else_clause)

    @_('WHILE "(" expr ")" "{" statement_list "}"')
    def statement(self, p):
        return ('while', p.expr, p.statement_list)

    @_('FUNCTION IDENTIFIER "(" param_list ")" "{" statement_list return_stmt "}"')
    def statement(self, p):
        return ('func', p.IDENTIFIER, p.param_list, p.statement_list, p.return_stmt)

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

    # Expressions
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

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return ('neg', p.expr)

    @_('FMINUS expr %prec UMINUS')
    def expr(self, p):
        return ('fneg', p.expr)

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