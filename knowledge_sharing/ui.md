# Language IDE — Compiler Design Project

A statically-typed, interpreted programming language built from scratch in Python,
with a desktop IDE powered by PySide6. Built as a team project for a Compiler Design course.

---

## What It Does

The project implements a complete language pipeline:

```
Source Code  →  Lexer  →  Parser  →  AST  →  Interpreter  →  Output
                                       ↑
                                  AST Viewer
                                  Memory Table
```

You write code in the built-in editor, hit **Run**, and the IDE simultaneously shows
the program output, the full Abstract Syntax Tree, and the memory state after execution.

---

## The Language

### Types

| Type | Example |
|---|---|
| Integer | `42`, `-7` |
| Float | `3.14`, `-0.5` |
| Boolean | `true`, `false` |
| String | `'hello'` |

Types are **inferred statically** — no explicit type declarations needed.
The interpreter enforces types at runtime; mixing types across operators is an error.

### Operators

Each type has its own dedicated operators — there is **no overloading**.

| Category | Operators |
|---|---|
| Integer arithmetic | `+`  `-`  `*`  `/` |
| Float arithmetic | `+.`  `-.`  `*.`  `/.` |
| Integer unary minus | `--` |
| Float unary minus | `--.` |
| String concatenation | `++` |
| Integer comparison | `==`  `!=` |
| Float comparison | `==.`  `!=.` |

Standard precedence applies: `*` and `/` bind tighter than `+` and `-`.
Parentheses override precedence as expected.

### Control Flow

```
if (x != 0) {
    print(x)
} else {
    print(0)
}

while (i != 10) {
    i = i + 1
}
```

### Functions

Value parameter passing — arguments are copied into an isolated local scope.
Changes to parameters inside a function never affect the caller's variables.

```
function add(a, b) {
    return a + b
}

result = add(3, 4)
print(result)
```

### Built-in

```
print(expr)    -- prints any value to the output panel
```

### Grammar (EBNF)

```ebnf
program     → statement*

statement   → IDENTIFIER '=' expr
            | 'if' '(' bool_expr ')' '{' statement* '}' ('else' '{' statement* '}')?
            | 'while' '(' bool_expr ')' '{' statement* '}'
            | 'print' '(' expr ')'
            | 'function' IDENTIFIER '(' param_list ')' '{' statement* return_stmt '}'
            | IDENTIFIER '(' arg_list ')'

bool_expr   → expr ('==' | '!=' | '==.' | '!=.') expr
            | BOOLEAN
            | IDENTIFIER

expr        → expr ('+' | '-' | '*' | '/') expr
            | expr ('+.' | '-.' | '*.' | '/.') expr
            | expr '++' expr
            | '--' expr
            | '--.' expr
            | '(' expr ')'
            | IDENTIFIER '(' arg_list ')'
            | IDENTIFIER
            | INTEGER | FLOAT | BOOLEAN | STRING

param_list  → (IDENTIFIER (',' IDENTIFIER)*)?
arg_list    → (expr (',' expr)*)?
return_stmt → ('return' expr)?
```

---

## Project Structure

```
project_root/
  main.py                  # Entry point
  src/
    lexer.py               # SLY-based tokeniser
    parser.py              # SLY-based LALR parser — emits AST nodes
    interpreter.py         # Tree-walk interpreter
    memory.py              # Scoped symbol table (singleton)
    ast/
      expression.py        # AST node classes for expressions
      statement.py         # AST node classes for statements
    ui/
      main_window.py       # QMainWindow — layout and run pipeline
      editor_widget.py     # Code editor with line numbers
      highlighter.py       # Syntax highlighter (QSyntaxHighlighter)
      ast_viewer.py        # AST tree display (QTreeWidget)
      memory_table.py      # Memory state display (QTableWidget)
      output_panel.py      # Program output display
    tests/
      test_ast.py          # Unit tests for AST node classes
      test_lexer.py        # Unit tests for the lexer
      test_parser.py       # Unit tests for parser output
      test_interpreter.py  # Integration tests for the interpreter
      test_memory.py       # Unit tests for the memory/scope system
```

---

## Setup & Running

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install dependencies
uv add PySide6

# Run the IDE
python main.py

# Run all tests
uv run pytest
```

---

## Key Design Decisions

### Separate operators per type
Rather than overloading `+` for integers, floats, and strings, the language uses
distinct operator tokens (`+`, `+.`, `++`). This makes type errors immediately visible
in the source code and simplifies the type-checking logic — the operator itself
determines the expected types of both operands.

### Class-based AST nodes
The AST uses a hierarchy of dataclasses (`ASTNode → Expression/Statement → concrete nodes`)
rather than tuples. This makes the interpreter's visitor pattern clean via Python's
`match`/`case` structural pattern matching, and makes the AST easy to display as a
tree in the IDE.

### No shadowing in Memory
The `Memory.set()` method walks up the scope stack to find an existing variable and
updates it in place. This means inner scopes (e.g. if/while bodies) can mutate outer
variables directly. For function calls, parameters are bound with `set_local()` which
always creates in the current scope, ensuring true pass-by-value isolation.

### Singleton Memory
`Memory` is a singleton so the interpreter and any future tools (e.g. a debugger or
type checker) all share one consistent view of program state without passing the
object around explicitly.

### Stdout capture for output
The interpreter's `print()` writes to Python's `sys.stdout`. The IDE temporarily
redirects `sys.stdout` to a `StringIO` buffer during execution, then writes the
captured output to the Output panel. This keeps the interpreter completely
UI-agnostic — it does not import anything from PySide6.

---

## IDE Features

| Feature | Detail |
|---|---|
| Syntax highlighting | Keywords, literals, operators, strings colourised |
| Line numbers | Painted in a gutter alongside the editor |
| AST viewer | Full expandable tree of every node in the parsed program |
| Memory table | Name, value, type, and scope depth for every live variable |
| Output panel | Program output in white, runtime errors in red |
| Status bar | Statement count and success/error status after each run |
| Keyboard shortcut | `Ctrl+Enter` to run, `Ctrl+L` to clear |
| Resizable panels | All panels separated by draggable splitters |

---

## Sample Programs

### Fibonacci (iterative)
```
a = 0
b = 1
n = 10
i = 0
while (i != n) {
    tmp = a + b
    a = b
    b = tmp
    i = i + 1
}
print(a)
```

### Factorial
```
function factorial(n) {
    result = 1
    i = 1
    while (i != n) {
        i = i + 1
        result = result * i
    }
    return result
}
print(factorial(5))
```

### Float arithmetic
```
pi = 3.14159
r = 5.0
area = pi *. r *. r
print(area)
```

### String operations
```
first = 'Hello'
last  = 'World'
full  = first ++ ', ' ++ last ++ '!'
print(full)
```

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| [Python 3.12+](https://python.org) | Implementation language |
| [SLY](https://github.com/dabeaz/sly) | Lexer and LALR parser generator |
| [PySide6](https://doc.qt.io/qtforpython) | Desktop UI framework (Qt6 bindings) |
| [pytest](https://pytest.org) | Test suite |
| [uv](https://github.com/astral-sh/uv) | Dependency management |