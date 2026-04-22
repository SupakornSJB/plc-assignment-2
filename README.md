# PLC Assignment 2

This project is a small compiler/interpreter assignment built around custom grammar and SLY:

## Project Overview

The language supported by this project includes:

- variable assignments
- `if` / `else` statements
- `while` loops
- `print` statements
- function declarations with parameters and optional return values
- integer, float, string, and boolean expressions

## Grammar

The language grammar is defined in [`grammar.txt`](./grammar.txt).

Some supported constructs include:

- `AssignmentStatement`
- `IfStatement`
- `WhileStatement`
- `PrintStatement`
- `FunctionDeclaration`
- arithmetic expressions for integers and floats
- string concatenation using `++`
- boolean comparisons such as:
    - `==`
    - `!=`
    - `==.`
    - `!=.`

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

Run the lexer directly:

```bash
uv run src/lexer.py
```

## Testing

Install dev dependencies and run tests:

```bash
uv sync --group dev
uv run pytest tests/ -v
```

Run a specific test:

```bash
uv run pytest tests/test_lexer.py::test_integer_literal -v
```
