# Interpreter — Knowledge Sharing

## Overview

The interpreter is a **tree-walk interpreter**: the parser builds an AST, then the
interpreter recursively walks it, evaluating each node and producing a result.

```
Source Code → [Lexer] → Tokens → [Parser] → AST → [Interpreter] → Output / Memory
```

---

## 1. What Does the Parser Return?

The parser (`src/parser.py`) reads tokens from the lexer and, as each grammar rule
matches, constructs an **AST node** and returns it upward. By the time `parse()`
finishes you have a single `Program` object — a tree of nested nodes.

**Source:**
```
x = 5
if (x != 3) { print(x) } else { x = 0 }
```

**AST the parser returns:**
```
Program([
    AssignmentStatement('x', IntegerLiteral(5)),
    IfStatement(
        condition = BinaryOp('!=', Identifier('x'), IntegerLiteral(3)),
        then_body = [PrintStatement(Identifier('x'))],
        else_body = [AssignmentStatement('x', IntegerLiteral(0))]
    )
])
```

Every node is a plain Python object — just data, no behaviour.  
Node classes live in `src/ast/expression.py` and `src/ast/statement.py`.

---

## 2. How the Interpreter Uses the AST

### The dispatcher — `visit()` (`src/interpreter.py:20`)

```python
def visit(self, node):
    match node:
        case Program():             self.visit_program(node)
        case IfStatement():         self.visit_if_statement(node)
        case BinaryOp():            return self.visit_binary_op(node)
        ...
```

`visit()` is the engine. Given any node it uses Python's `match` to route to the
correct handler method. The tree is walked **recursively** — visiting a parent
triggers visits to its children.

This replaces the older dynamic-dispatch approach (`getattr(self, f'visit_{type(node).__name__}')`) with an explicit match statement. The advantage is that all handled node types are visible in one place.

---

## 3. Is This the Standard Approach?

Yes — this is called a **tree-walk interpreter** and is the standard first
implementation taught in compilers courses and used in production for simple
languages.

The pattern maps almost 1:1 to Robert Nystrom's *Crafting Interpreters*
(Chapters 7–11), which is the standard pedagogical reference.

| This implementation | Production interpreters add |
|---|---|
| Python dict for memory | Proper closures capturing environment at definition time |
| Type check at runtime | Static type-checking pass before execution |
| `return_expr` after body | `ReturnException` to unwind mid-body early returns |

---

## 4. Why `entry['value']` in `visit_function_call` (`src/interpreter.py:81`)

`Memory.get` (`src/memory.py:26`) does not return the raw value — it returns the
full internal record:

```python
# memory.py — what set() stores
scope[variable_name] = {"value": value, "data_type": data_type}
```

So `memory.get("add")` returns:
```python
{"value": <FunctionDeclaration node>, "data_type": "function"}
```

`entry['value']` unwraps the actual node from that envelope. Every variable —
integers, strings, booleans, functions — goes through the same wrapper. The same
unwrap happens in `visit_identifier` (`src/interpreter.py:145`):

```python
def visit_identifier(self, node: Identifier):
    return self.memory.get(node.name)['value']
```

The `data_type` field is stored alongside for the memory table display
(`Memory.__repr__`) and for the `_require_*` type guards.

---

## 5. What Does `zip` Do in the Params Loop (`src/interpreter.py:90`)

`zip` pairs parameter names with argument values by position:

```python
func.params = ['a', 'b']
args        = [4,   5  ]

zip(func.params, args) → [('a', 4), ('b', 5)]
```

The loop then binds each name to its value in the function's local scope:

```python
for param, val in zip(func.params, args):
    self.memory._current[param] = {"value": val, "data_type": self._type_of(val)}
```

Note: `_current` is used directly (not `memory.set`) so that parameters are written
into the **innermost scope** and don't overwrite outer variables with the same name.
See section 7 for why this matters.

`zip` silently stops at the shorter list — this is why the arity check
(`len(args) != len(func.params)`) must come before the loop.

---

## 6. What Does `Memory.__repr__` Do (`src/memory.py:45`)

`__repr__` is a Python dunder method that defines how an object prints itself when
you call `print(memory)` or `str(memory)`. The implementation builds a formatted
table of every variable in every scope:

```
Name    Value   Data Type
------------------------------
[global]
x       99      int
flag    True    bool
[scope 1]
i       3       int
------------------------------
```

It loops through `self.scopes`, labels index 0 as `"global"` and the rest as
`"scope 1"`, `"scope 2"` etc., then lists each variable's name, value, and type.
Purely for debugging — the interpreter's `__main__` block prints it at the end.

---

## 7. What Does `reversed` Do in Memory (`src/memory.py:27`)

```python
for scope in reversed(self.scopes):
```

`reversed` iterates the scope stack from **last to first**, so the innermost
(most recently pushed) scope is checked before outer ones:

```python
self.scopes = [
    {'x': ...},   # index 0 — global  (checked last)
    {'i': ...},   # index 1 — inner   (checked first)
]
```

This is correct for `get` — it finds the nearest variable.

For `set`, the same traversal means an assignment **updates the variable wherever
it already lives**, rather than creating a new one in the current scope. This is
intentional for `if`/`while` (you want `i = i + 1` inside a while loop to update
the outer `i`), but was a bug for function parameters (see section 8).

---

## 8. Why `if`/`while` Scoping Works but Function Params Didn't

### `if` / `while` — correct behaviour

Assignments inside a block intentionally reach outward:

```
i = 0
while (i != 5) {
    i = i + 1   ← must update the outer i, otherwise infinite loop
}
```

`memory.set('i', ...)` walks outward, finds `i` in the outer scope, updates it
there. This is the desired behaviour.

### Function parameters — was a bug, now fixed

You would expect calling `f(10)` below to leave the outer `a` unchanged:

```
a = 1
function f(a) { a = 99 }
f(10)
print(a)   ← should print 1, not 99
```

Before the fix, `memory.set('a', 10)` walked outward, found `a` in global, and
updated it there. The parameter never lived locally.

**The fix** (`src/interpreter.py:90`) — write parameters directly to `_current`
(the innermost scope), bypassing the outward traversal entirely:

```python
# Before (wrong — would update outer 'a')
self.memory.set(param, val, self._type_of(val))

# After (correct — always creates a local binding)
self.memory._current[param] = {"value": val, "data_type": self._type_of(val)}
```

| Construct | Should update outer variables? | How |
|---|---|---|
| `if` / `while` body | Yes | `memory.set()` — walks outward |
| Function parameters | No — must be local | `memory._current` — direct write |

---

## 9. Can Type Checking Be Done in the Parser? (Syntax-Directed Translation)

Yes — this is called **syntax-directed interpretation**: each parser rule evaluates
immediately instead of building a node.

```python
@_('expr INTEGER_ADDITION expr')
def expr(self, p):
    return p.expr0 + p.expr1   # evaluate now, return int
```

The fundamental problem with `if`/`while` is that SLY reduces rules bottom-up, so
the body is fully evaluated *before* the `if` rule fires. You cannot skip the else
branch or loop the body without using thunks (deferred lambdas), which makes the
approach awkward.

**Recommendation:** keep the separate interpreter. It allows multiple passes
(type-check, then run), AST reuse (pretty-printer, optimizer), and handles
`while` loops naturally.

```
Source → Lexer → Parser → AST → [Type Checker] → [Interpreter]
                                       ↑
                               future addition:
                               catches errors before execution
```