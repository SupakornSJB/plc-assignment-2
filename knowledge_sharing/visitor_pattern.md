# Visitor Pattern — Knowledge Sharing

## What is it?

The Visitor Pattern is a way to **separate an algorithm from the data structure it operates on**. Instead of putting logic inside each node class, you write a separate `Visitor` class whose methods define what to do when visiting each node type.

In the context of a compiler/interpreter, this means:

- **AST Nodes** — just hold data, no logic
- **Visitor** — holds all the logic, walks the tree

---

## Why Use It Here?

Our compiler is split into three stages:

```
Source Code → [Lexer] → Tokens → [Parser] → AST → [Translator] → Result
```

The Visitor Pattern is the contract between the **Parser** and the **Translator**:
- Parser builds the AST (tree of nodes)
- Translator visits each node and executes logic

This lets both sides work **independently** — as long as they agree on the node types.

---

## The Components

### 1. AST Nodes (Data only, no logic)

Each grammar rule maps to a node class. Nodes just store their children.

```python
# Base class
class Node:
    pass

# AssignmentStatement → IDENTIFIER "=" Expression
class AssignmentNode(Node):
    def __init__(self, name, expr):
        self.name = name    # string (variable name)
        self.expr = expr    # Node (the expression)

# IntExpression → IntExpression "+" IntTerm
class IntBinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left    # Node
        self.op = op        # string: '+', '-', '*', '/'
        self.right = right  # Node

# IntFactor → INTEGER
class IntLiteralNode(Node):
    def __init__(self, value):
        self.value = value  # int

# IfStatement → "if" "(" BooleanExpression ")" "{" StatementList "}" ElseClause
class IfNode(Node):
    def __init__(self, condition, body, else_body):
        self.condition = condition  # Node
        self.body = body            # list of Nodes
        self.else_body = else_body  # list of Nodes | None

# FunctionDeclaration → "function" IDENTIFIER "(" ParameterList ")" "{" StatementList ReturnStatement "}"
class FunctionDeclNode(Node):
    def __init__(self, name, params, body, return_stmt):
        self.name = name              # string
        self.params = params          # list of strings
        self.body = body              # list of Nodes
        self.return_stmt = return_stmt  # Node | None

# ReturnStatement → "return" Expression | ε
class ReturnNode(Node):
    def __init__(self, expr):
        self.expr = expr  # Node | None (None = void return)
```

---

### 2. The Parser Builds the Tree

The parser's only job is to return node objects. No evaluation, no logic.

```python
from sly import Parser

class MyParser(Parser):

    @_('IDENTIFIER EQUALS expression')
    def statement(self, p):
        return AssignmentNode(p.IDENTIFIER, p.expression)  # just build and return

    @_('int_expression PLUS int_term')
    def int_expression(self, p):
        return IntBinaryOpNode(p.int_expression, '+', p.int_term)

    @_('INTEGER')
    def int_factor(self, p):
        return IntLiteralNode(p.INTEGER)

    @_('IF LPAREN bool_expression RPAREN LBRACE statement_list RBRACE else_clause')
    def if_statement(self, p):
        return IfNode(p.bool_expression, p.statement_list, p.else_clause)

    @_('ELSE LBRACE statement_list RBRACE')
    def else_clause(self, p):
        return p.statement_list

    @_('')
    def else_clause(self, p):
        return None  # no else
```

---

### 3. The Visitor Walks the Tree

The visitor has one method per node type, named `visit_<NodeClassName>`.

```python
class Interpreter:

    def __init__(self):
        self.variables = {}  # symbol table

    # Entry point — dispatches to the correct visit method
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.visit_unknown)
        return method(node)

    def visit_unknown(self, node):
        raise Exception(f'No visitor for node type: {type(node).__name__}')

    # Visit a list of statements
    def visit_list(self, stmts):
        result = None
        for stmt in stmts:
            result = self.visit(stmt)
        return result

    # AssignmentNode
    def visit_AssignmentNode(self, node):
        value = self.visit(node.expr)
        self.variables[node.name] = value

    # IntBinaryOpNode
    def visit_IntBinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op == '/': return left // right

    # IntLiteralNode
    def visit_IntLiteralNode(self, node):
        return node.value

    # IfNode
    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        if condition:
            self.visit_list(node.body)
        elif node.else_body is not None:
            self.visit_list(node.else_body)

    # ReturnNode
    def visit_ReturnNode(self, node):
        if node.expr is None:
            return None  # void return
        return self.visit(node.expr)
```

---

## Putting It Together

```python
source_code = """
x = 1 + 2
if (x == 3) {
    print(x)
} else {
    print(0)
}
"""

lexer = MyLexer()
parser = MyParser()
interpreter = Interpreter()

tokens = lexer.tokenize(source_code)  # Lexer produces tokens
ast = parser.parse(tokens)            # Parser produces AST
interpreter.visit_list(ast)           # Translator walks the tree
```

---

## How `visit()` Dispatch Works

```
interpreter.visit(IfNode(...))
    → method_name = "visit_IfNode"
    → calls self.visit_IfNode(node)
        → self.visit(node.condition)   # recurse into condition
        → self.visit_list(node.body)   # recurse into body
```

This is called **dynamic dispatch** — the method called depends on the runtime type of the node, not a hardcoded `if/elif` chain.

---

## Summary

| Component | Responsibility |
|-----------|---------------|
| **Node classes** | Store data, no logic |
| **Parser** | Build and return nodes |
| **`visit(node)`** | Dispatch to the right method |
| **`visit_XNode()`** | Logic for that specific node type |
