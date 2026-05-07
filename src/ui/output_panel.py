from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QColor, QTextCharFormat, QFont


class OutputPanel(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        font = QFont('Courier New', 11)
        self.setFont(font)
        self.setStyleSheet('background: #1E1E1E; color: #D4D4D4;')

    def write_output(self, text: str) -> None:
        self.appendPlainText(text)

    def write_error(self, text: str) -> None:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor('#F44747'))
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text + '\n', fmt)

    def clear_display(self) -> None:
        self.clear()