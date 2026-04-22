from sly import Lexer

class LanguageLexer(Lexer):
    def __init__(self):
        super().__init__()
        self.is_lexical_error = False

    ### tokens ###
    tokens = {
        # Keywords
        IF, ELSE, WHILE, PRINT, FUNCTION, RETURN,
        # Integer
        INTEGER,
        INTEGER_ADDITION, INTEGER_SUBTRACTION, INTEGER_MULTIPLICATION, INTEGER_DIVISION,
        INTEGER_UMINUS, INTEGER_EQUALITY, INTEGER_INEQUALITY,
        # Float
        FLOAT,
        FLOAT_ADDITION, FLOAT_SUBTRACTION, FLOAT_MULTIPLICATION, FLOAT_DIVISION,
        FLOAT_UMINUS, FLOAT_EQUALITY, FLOAT_INEQUALITY,
        # Boolean
        BOOLEAN,
        # String
        STRING, STRING_CONCAT,
        # Symbols
        PAREN_OPEN, PAREN_CLOSE, BRACE_OPEN, BRACE_CLOSE, COMMA,
        # Misc
        IDENTIFIER, ASSIGNMENT,
    }

    ignore = ' \t'

    # Keywords
    IF = r'if\b'
    ELSE = r'else\b'
    WHILE = r'while\b'
    PRINT = r'print\b'
    FUNCTION = r'function\b'
    RETURN = r'return\b'

    # Float + Arithmetics (longer patterns first)
    FLOAT = r'\d+\.\d+'
    FLOAT_UMINUS = r'\-\-\.'
    FLOAT_EQUALITY = r'==\.'
    FLOAT_INEQUALITY = r'!=\.'
    FLOAT_ADDITION = r'\+\.'
    FLOAT_SUBTRACTION = r'\-\.'
    FLOAT_MULTIPLICATION = r'\*\.'
    FLOAT_DIVISION = r'\/\.'

    # String
    STRING_CONCAT = r'\+\+'
    STRING = r"'[^']*'"

    # Integer + Arithmetics (longer patterns first)
    INTEGER = r'\d+'
    INTEGER_UMINUS = r'\-\-'
    INTEGER_EQUALITY = r'=='
    INTEGER_INEQUALITY = r'!='
    INTEGER_ADDITION = r'\+'
    INTEGER_SUBTRACTION = r'\-'
    INTEGER_MULTIPLICATION = r'\*'
    INTEGER_DIVISION = r'\/'

    # Boolean
    BOOLEAN = r'true\b|false\b'

    # Symbols
    PAREN_OPEN = r'\('
    PAREN_CLOSE = r'\)'
    BRACE_OPEN = r'\{'
    BRACE_CLOSE = r'\}'
    COMMA = r','

    # Misc
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ASSIGNMENT = r'='

    # Extra action for newlines
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    def BOOLEAN(self, t):
        t.value = t.value == 'true'
        return t

    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    def error(self, t):
        self.is_lexical_error = True
        self.index += 1
        print(f"ERROR: Illegal character '{t.value[0]}' at line {self.lineno}")


if __name__ == '__main__':
    # Write a simple test that only run when you execute this file
    string_input: str = '''
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

        print(z)
        print(s)

        function add(p, q) {
            return p + q
        }
    '''

    lex = LanguageLexer()
    for token in lex.tokenize(string_input):
        print(token)
