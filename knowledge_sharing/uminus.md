# Handling UMINUS (Unary Minus)

## What is UMINUS?

UMINUS is **unary minus** — a negation applied to a single operand, not a subtraction between two values.

```
-5        ← UMINUS, negates the integer 5
-3.14     ← UMINUS, negates the float 3.14
-x        ← UMINUS, negates the value of variable x
-(1 + 2)  ← UMINUS, negates the result of an expression
```

The challenge is that `-` is also used for **binary subtraction** (`1 - 2`), so the lexer produces the same `-` token for both cases. It's the **parser's job** to tell them apart by context.

---

## In the Grammar

UMINUS is added at the `Factor` level because it has the **highest precedence** — it binds tighter than `*`, `/`, `+`, `-`.

```
IntFactor → INTEGER
          | IDENTIFIER
          | "(" IntExpression ")"
          | "-" IntFactor          ← UMINUS (recursive, allows --x)

FloatFactor → FLOAT
            | IDENTIFIER
            | "(" FloatExpression ")"
            | "-." FloatFactor     ← UMINUS for float
```

Placing it in `Factor` (not `Term` or `Expression`) ensures correct precedence:

```
-2 * 3   →  (-2) * 3   ✅  (UMINUS binds tighter than *)
-(1 + 2) →  -(3)       ✅  (parentheses evaluated first, then negated)
--5      →  -(-5) = 5  ✅  (recursive, double negation works)
```

---

## The AST Node

```python
# "-" IntFactor
class UnaryMinusIntNode(Node):
    def __init__(self, operand):
        self.operand = operand  # Node

# "-." FloatFactor
class UnaryMinusFloatNode(Node):
    def __init__(self, operand):
        self.operand = operand  # Node
```

---

## In SLY — The Problem

`MINUS` is used for both binary subtraction and UMINUS:

```python
# Binary subtraction — MINUS used here
@_('int_expression MINUS int_term')
def int_expression(self, p):
    return IntBinaryOpNode(p.int_expression, '-', p.int_term)

# Unary minus — MINUS also used here
@_('MINUS int_factor')
def int_factor(self, p):
    return UnaryMinusIntNode(p.int_factor)
```

This creates a **precedence conflict** — when the parser sees `MINUS`, it doesn't know which rule to apply. Without guidance, it would give UMINUS the same precedence as binary `-`, causing wrong parse trees:

```
1 + -2   →  parsed as  (1 + -) 2  ❌ (wrong)
           should be   1 + (-2)   ✅
```

---

## In SLY — The Fix (`%prec`)

Declare a `UMINUS` pseudo-token in the precedence table with **higher precedence** than binary operators, then tag the rule with `%prec UMINUS`:

```python
class MyParser(Parser):

    precedence = (
        ('right', ELSE),                    # for dangling else
        ('left', PLUS, MINUS),              # lowest among arithmetic
        ('left', TIMES, DIVIDE),            # higher than +/-
        ('right', UMINUS),                  # highest — applied last, binds tightest
    )

    # Binary subtraction — uses MINUS precedence (left, level 2)
    @_('int_expression MINUS int_term')
    def int_expression(self, p):
        return IntBinaryOpNode(p.int_expression, '-', p.int_term)

    # Unary minus — override to use UMINUS precedence (right, level 4)
    @_('MINUS int_factor %prec UMINUS')
    def int_factor(self, p):
        return UnaryMinusIntNode(p.int_factor)
```

`%prec UMINUS` tells SLY: *"use the precedence of `UMINUS` for this rule, not the precedence of `MINUS`"*.

`UMINUS` is **not a real token** — it never appears in the lexer. It's a virtual marker only used to assign a precedence level.

### Float UMINUS

```python
    # Float unary minus — uses a separate operator "-."
    @_('MINUSDOT float_factor')
    def float_factor(self, p):
        return UnaryMinusFloatNode(p.float_factor)
```

Since float uses `-.` (a distinct token from `-`), there's **no ambiguity** with float binary subtraction (`-. `is always unary or binary float minus). No `%prec` trick needed for floats.

---

## In the Visitor

```python
# Negate an integer expression
def visit_UnaryMinusIntNode(self, node):
    value = self.visit(node.operand)
    return -value

# Negate a float expression
def visit_UnaryMinusFloatNode(self, node):
    value = self.visit(node.operand)
    return -value
```

---

## Full Example

### Source
```
x = -5
y = -(1 + 2)
z = --3
a = -. 3.14
```

### AST
```
AssignmentNode("x", UnaryMinusIntNode(IntLiteralNode(5)))
AssignmentNode("y", UnaryMinusIntNode(IntBinaryOpNode(IntLiteralNode(1), '+', IntLiteralNode(2))))
AssignmentNode("z", UnaryMinusIntNode(UnaryMinusIntNode(IntLiteralNode(3))))
AssignmentNode("a", UnaryMinusFloatNode(FloatLiteralNode(3.14)))
```

### Visitor Execution
```
visit(UnaryMinusIntNode(IntLiteralNode(5)))
  → visit(IntLiteralNode(5))  →  5
  → -5

visit(UnaryMinusIntNode(IntBinaryOpNode(...)))
  → visit(IntBinaryOpNode(1, '+', 2))  →  3
  → -3

visit(UnaryMinusIntNode(UnaryMinusIntNode(IntLiteralNode(3))))
  → visit(UnaryMinusIntNode(IntLiteralNode(3)))
      → visit(IntLiteralNode(3))  →  3
      → -3
  → -(-3) = 3
```

---

## Summary

| Concern | Solution |
|---------|----------|
| Grammar | Add `"-" IntFactor` production at `Factor` level |
| Precedence conflict with binary `-` | Use `%prec UMINUS` pseudo-token in SLY |
| Float UMINUS | Use distinct `-.` token, no conflict |
| AST Node | `UnaryMinusIntNode`, `UnaryMinusFloatNode` |
| Visitor | Evaluate operand, negate and return |
