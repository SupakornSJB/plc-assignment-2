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
