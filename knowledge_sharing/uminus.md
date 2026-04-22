# Handling UMINUS (Unary Minus)

## What is UMINUS?

UMINUS is **unary minus** — a negation applied to a single operand, not a subtraction between two values.

```
--5        ← UMINUS, negates the integer 5
--.3.14    ← UMINUS, negates the float 3.14
--x        ← UMINUS, negates the value of variable x
--(1 + 2)  ← UMINUS, negates the result of an expression
```

The challenge is that `-` is also used for **binary subtraction** (`1 - 2`). To avoid ambiguity, our grammar uses **explicit double-minus tokens** (`--` and `--.`) for unary negation instead of reusing the single `-`.

---

## In the Grammar

Integer UMINUS uses `"--"` at the `IntFactor` level (highest precedence — binds tighter than `*`, `/`, `+`, `-`):

```
IntFactor → INTEGER
          | IDENTIFIER
          | "(" IntExpression ")"
          | "--" IntFactor          ← UMINUS (recursive, allows ----x)
```

Float UMINUS uses `"--."` at the `FloatTerm` level:

```
FloatTerm → FloatTerm "*." FloatFactor
          | FloatTerm "/." FloatFactor
          | FloatFactor
          | "--." FloatTerm         ← UMINUS for float
```

Using `"--"` and `"--."` as distinct tokens from `-` and `-.` means the lexer produces different tokens for unary vs. binary minus — no parser-level ambiguity.

Precedence examples:

```
--2 * 3    →  (--2) * 3   ✅  (UMINUS at IntFactor binds tighter than *)
--(1 + 2)  →  -(3)        ✅  (parentheses evaluated first, then negated)
----5      →  -(-(-(-5)))  ✅  (recursive, quadruple negation works)
```

---

## The AST Node

```python
# "--" IntFactor
class UnaryMinusIntNode(Node):
    def __init__(self, operand):
        self.operand = operand  # Node

# "--." FloatTerm
class UnaryMinusFloatNode(Node):
    def __init__(self, operand):
        self.operand = operand  # Node
```

---

## In SLY

Since `"--"` and `"--."` are dedicated tokens (distinct from `-` and `-.`), there is **no precedence conflict** — no `%prec UMINUS` trick is needed.

```python
# Binary subtraction — MINUS token
@_('int_expression MINUS int_term')
def int_expression(self, p):
    return IntBinaryOpNode(p.int_expression, '-', p.int_term)

# Unary minus — DOUBLEMINUS token, no conflict
@_('DOUBLEMINUS int_factor')
def int_factor(self, p):
    return UnaryMinusIntNode(p.int_factor)
```

### Float UMINUS

```python
# Float unary minus — DOUBLEMINUSDOT token
@_('DOUBLEMINUSDOT float_term')
def float_term(self, p):
    return UnaryMinusFloatNode(p.float_term)
```

Float UMINUS applies to `float_term` (not `float_factor`), matching the grammar placement.

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
x = --5
y = --(1 + 2)
z = ----3
a = --. 3.14
```

### AST
```
AssignmentNode("x", UnaryMinusIntNode(IntLiteralNode(5)))
AssignmentNode("y", UnaryMinusIntNode(IntBinaryOpNode(IntLiteralNode(1), '+', IntLiteralNode(2))))
AssignmentNode("z", UnaryMinusIntNode(UnaryMinusIntNode(UnaryMinusIntNode(UnaryMinusIntNode(IntLiteralNode(3))))))
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
| Grammar (int) | `"--" IntFactor` production at `IntFactor` level |
| Grammar (float) | `"--." FloatTerm` production at `FloatTerm` level |
| Ambiguity with binary `-` | Avoided by using distinct `"--"` / `"--."` tokens |
| Precedence trick | Not needed — no token overlap |
| AST Node | `UnaryMinusIntNode`, `UnaryMinusFloatNode` |
| Visitor | Evaluate operand, negate and return |