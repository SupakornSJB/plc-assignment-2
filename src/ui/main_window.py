import io
import sys

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QPushButton, QLabel, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence

from src.lexer import LanguageLexer
from src.parser import LanguageParser
from src.interpreter import Interpreter
from src.memory import Memory

from src.ui.editor_widget import CodeEditor
from src.ui.ast_viewer import ASTViewer
from src.ui.memory_table import MemoryTable
from src.ui.output_panel import OutputPanel


STYLESHEET = """
QMainWindow, QWidget {
    background: #1E1E1E;
    color: #D4D4D4;
    font-family: 'Segoe UI', sans-serif;
}
QPushButton {
    background: #0E639C;
    color: white;
    border: none;
    padding: 6px 18px;
    border-radius: 3px;
    font-size: 13px;
}
QPushButton:hover  { background: #1177BB; }
QPushButton:pressed { background: #0A4F7E; }
QPushButton#clear_btn {
    background: #3C3C3C;
}
QPushButton#clear_btn:hover { background: #505050; }
QSplitter::handle { background: #3C3C3C; }
QLabel {
    color: #858585;
    font-size: 11px;
    padding: 2px 6px;
}
QHeaderView::section {
    background: #252526;
    color: #D4D4D4;
    border: 1px solid #3C3C3C;
    padding: 4px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Language IDE')
        self.resize(1280, 720)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._connect_signals()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Toolbar
        self._run_btn   = QPushButton('▶  Run')
        self._clear_btn = QPushButton('Clear')
        self._clear_btn.setObjectName('clear_btn')

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 6, 8, 6)
        toolbar_layout.addWidget(self._run_btn)
        toolbar_layout.addWidget(self._clear_btn)
        toolbar_layout.addStretch()

        # Panels
        self._editor  = CodeEditor()
        self._output  = OutputPanel()
        self._ast     = ASTViewer()
        self._memory  = MemoryTable()

        # Label each right-side panel
        def labeled(title: str, widget: QWidget) -> QWidget:
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)
            label = QLabel(title.upper())
            label.setStyleSheet('color: #569CD6; font-weight: bold; font-size: 10px; padding: 4px 6px;')
            layout.addWidget(label)
            layout.addWidget(widget)
            return container

        # Right column: Output on top, AST in middle, Memory at bottom
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(labeled('Output', self._output))
        right_splitter.addWidget(labeled('AST', self._ast))
        right_splitter.addWidget(labeled('Memory', self._memory))
        right_splitter.setSizes([200, 300, 200])

        # Main horizontal split: editor | right panels
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(labeled('Editor', self._editor))
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([600, 600])

        # Root layout
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(toolbar)
        root_layout.addWidget(main_splitter)
        self.setCentralWidget(root)

        # Status bar
        self._status = QStatusBar()
        self._status.setStyleSheet('color: #858585; font-size: 11px;')
        self.setStatusBar(self._status)
        self._status.showMessage('Ready')

    def _connect_signals(self):
        self._run_btn.clicked.connect(self._run)
        self._clear_btn.clicked.connect(self._clear)
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self._run)
        QShortcut(QKeySequence('Ctrl+L'),      self).activated.connect(self._clear)

    # ── Run Pipeline ──────────────────────────────────────────────────────────

    def _run(self):
        source = self._editor.toPlainText().strip()
        if not source:
            self._status.showMessage('Nothing to run.')
            return

        self._output.clear_display()
        self._ast.clear_display()
        self._memory.clear_display()

        # ── Step 1: Lex + Parse ───────────────────────────────────────────────
        try:
            lexer  = LanguageLexer()
            parser = LanguageParser()
            tree   = parser.parse(lexer.tokenize(source))
            if tree is None:
                self._output.write_error('Parse error: could not build AST.')
                self._status.showMessage('❌  Parse error')
                return
        except Exception as e:
            self._output.write_error(f'Parse error: {e}')
            self._status.showMessage('❌  Parse error')
            return

        # ── Step 2: Show AST ──────────────────────────────────────────────────
        self._ast.display(tree)

        # ── Step 3: Interpret, capture stdout ─────────────────────────────────
        Memory().reset()          # requires Memory.reset() from earlier PR review
        interp  = Interpreter()
        capture = io.StringIO()
        try:
            sys.stdout = capture
            interp.visit(tree)
        except Exception as e:
            sys.stdout = sys.__stdout__
            self._output.write_error(f'Runtime error: {e}')
            self._status.showMessage('❌  Runtime error')
        else:
            sys.stdout = sys.__stdout__
            output = capture.getvalue()
            if output:
                self._output.write_output(output.rstrip())
            else:
                self._output.write_output('(no output)')
            stmt_count = len(tree.statements)
            self._status.showMessage(
                f'✅  Ran successfully  ·  {stmt_count} top-level statement{"s" if stmt_count != 1 else ""}'
            )
        finally:
            sys.stdout = sys.__stdout__

        # ── Step 4: Show memory ───────────────────────────────────────────────
        self._memory.display(interp.memory)

    def _clear(self):
        self._editor.clear()
        self._output.clear_display()
        self._ast.clear_display()
        self._memory.clear_display()
        self._status.showMessage('Ready')