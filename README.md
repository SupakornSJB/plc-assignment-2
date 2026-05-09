# PLC Assignment 2

A small compiler/interpreter for a custom language, built with Python and [SLY](https://github.com/dabeaz/sly).

## Pipeline

```
Source Code → [Lexer] → Tokens → [Parser] → AST → [Semantic Analyzer] → [Interpreter] → Output / Memory
```

| Stage | File | Description |
|---|---|---|
| Lexer | `src/lexer.py` | Tokenises source into typed tokens |
| Parser | `src/parser.py` | Builds an AST from tokens |
| AST Nodes | `src/ast_node/expression.py`, `src/ast_node/statement.py` | Data classes for the tree |
| Semantic Analyzer | `src/semantic_analyzer.py` | Validates function declarations, and variable existence before execution |
| Memory | `src/memory.py` | Scoped symbol table (singleton) |
| Interpreter | `src/interpreter.py` | Tree-walk interpreter; produces output and final memory state |

## Language Features

- Variable assignments
- `if` / `else` statements
- `while` loops
- `print` statements
- Function declarations with parameters and optional return values
- Integer, float, string, and boolean expressions
- Type enforcement — operands are checked at runtime (e.g. `+` requires both sides to be `int`)

### Operators

| Category | Operators |
|---|---|
| Integer arithmetic | `+` `-` `*` `/` |
| Float arithmetic | `+.` `-.` `*.` `/.` |
| Integer negation | `--` |
| Float negation | `--.` |
| String concat | `++` |
| Integer comparison | `==` `!=` |
| Float comparison | `==.` `!=.` |

The full grammar is in [`grammar.txt`](./grammar.txt).

## Setup

Requires [uv](https://docs.astral.sh/uv/). Install it with:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Install dependencies:

```bash
uv sync
```

## Running

Run the parser (prints the AST):

```bash
uv run src/parser.py
# or
uv run -m src.parser
```

Run the interpreter (prints output and final memory state):

```bash
uv run src/interpreter.py
# or
uv run -m src.interpreter
```

Run the lexer:

```bash
uv run src/lexer.py
# or
uv run -m src.lexer
```

Run the UI:

```bash
uv run main.py
```

## Testing

```bash
uv sync --group dev
uv run pytest -v
```

Run a specific test file:

```bash
uv run pytest tests/test_interpreter.py -v
```

Run a specific test:

```bash
uv run pytest tests/test_lexer.py::test_integer_literal -v
```

### Test coverage

| File | What it tests |
|---|---|
| `tests/test_lexer.py` | Token recognition, keyword mapping, error flag |
| `tests/test_ast.py` | AST node construction |
| `tests/test_memory.py` | Scoped symbol table, singleton, type enforcement on reassignment |
| `tests/test_parser.py` | AST structure produced by the parser |
| `tests/test_interpreter.py` | End-to-end execution, type mismatch errors, Fibonacci |
| `tests/test_function.py` | Semantic analyzer — function declarations, arity, undefined names |

## Knowledge Sharing

| Doc | Topic |
|---|---|
| [`knowledge_sharing/interpreter.md`](./knowledge_sharing/interpreter.md) | How the interpreter works, visitor dispatch, memory scoping, type checking |
| [`knowledge_sharing/visitor_pattern.md`](./knowledge_sharing/visitor_pattern.md) | Visitor pattern — AST nodes, parser, and translator |
| [`knowledge_sharing/uminus.md`](./knowledge_sharing/uminus.md) | Unary negation operators (`--` and `--.`) |
| [`knowledge_sharing/ui.md`](./knowledge_sharing/ui.md) | PySide6 IDE — layout, panels, run pipeline, syntax highlighting |