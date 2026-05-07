from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QColor, QBrush

from src.ast.expression import (
    BinaryOp, UnaryOp, FunctionCall, Identifier,
    IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral,
)
from src.ast.statement import (
    Program, AssignmentStatement, IfStatement, WhileStatement,
    PrintStatement, FunctionDeclaration,
)

# Color scheme per node category
NODE_COLORS = {
    'statement':  '#569CD6',
    'expression': '#4EC9B0',
    'literal':    '#B5CEA8',
    'operator':   '#DCDCAA',
}


def _colored_item(parent, text: str, category: str) -> QTreeWidgetItem:
    item = QTreeWidgetItem(parent, [text])
    item.setForeground(0, QBrush(QColor(NODE_COLORS.get(category, '#D4D4D4'))))
    return item


def _build_item(parent, node) -> None:
    """Recursively build tree items from an AST node."""

    match node:
        case Program():
            item = _colored_item(parent, 'Program', 'statement')
            for stmt in node.statements:
                _build_item(item, stmt)

        case AssignmentStatement():
            item = _colored_item(parent, f'Assign  {node.identifier}', 'statement')
            _build_item(item, node.expr)

        case PrintStatement():
            item = _colored_item(parent, 'Print', 'statement')
            _build_item(item, node.expr)

        case IfStatement():
            item = _colored_item(parent, 'If', 'statement')
            cond = _colored_item(item, 'condition', 'expression')
            _build_item(cond, node.condition)
            then = _colored_item(item, 'then', 'statement')
            for s in node.then_body:
                _build_item(then, s)
            if node.else_body:
                else_ = _colored_item(item, 'else', 'statement')
                for s in node.else_body:
                    _build_item(else_, s)

        case WhileStatement():
            item = _colored_item(parent, 'While', 'statement')
            cond = _colored_item(item, 'condition', 'expression')
            _build_item(cond, node.condition)
            body = _colored_item(item, 'body', 'statement')
            for s in node.body:
                _build_item(body, s)

        case FunctionDeclaration():
            params = ', '.join(node.params) or '—'
            item = _colored_item(parent, f'FuncDecl  {node.name}({params})', 'statement')
            body = _colored_item(item, 'body', 'statement')
            for s in node.body:
                _build_item(body, s)
            if node.return_expr:
                ret = _colored_item(item, 'return', 'statement')
                _build_item(ret, node.return_expr)

        case BinaryOp():
            item = _colored_item(parent, f'BinaryOp  {node.op}', 'operator')
            _build_item(item, node.left)
            _build_item(item, node.right)

        case UnaryOp():
            item = _colored_item(parent, f'UnaryOp  {node.op}', 'operator')
            _build_item(item, node.operand)

        case FunctionCall():
            item = _colored_item(parent, f'Call  {node.name}', 'expression')
            for arg in node.args:
                _build_item(item, arg)

        case Identifier():
            _colored_item(parent, f'Var  {node.name}', 'expression')

        case IntegerLiteral():
            _colored_item(parent, f'Int  {node.value}', 'literal')

        case FloatLiteral():
            _colored_item(parent, f'Float  {node.value}', 'literal')

        case StringLiteral():
            _colored_item(parent, f"Str  '{node.value}'", 'literal')

        case BooleanLiteral():
            _colored_item(parent, f'Bool  {node.value}', 'literal')

        case _:
            _colored_item(parent, f'Unknown  {type(node).__name__}', 'literal')


class ASTViewer(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel('AST')
        self.setStyleSheet('background: #1E1E1E; color: #D4D4D4;')

    def display(self, tree: Program) -> None:
        self.clear()
        _build_item(self.invisibleRootItem(), tree)
        self.expandAll()

    def clear_display(self) -> None:
        self.clear()