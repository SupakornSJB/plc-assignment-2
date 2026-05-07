from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


SCOPE_COLORS = ['#1E1E1E', '#252526', '#2D2D2D']  # alternating per scope depth


class MemoryTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Name', 'Value', 'Type', 'Scope'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setStyleSheet('background: #1E1E1E; color: #D4D4D4; gridline-color: #3C3C3C;')
        self.verticalHeader().setVisible(False)

    def display(self, memory) -> None:
        self.setRowCount(0)
        for depth, scope in enumerate(memory.scopes):
            label = 'global' if depth == 0 else f'scope {depth}'
            bg = QColor(SCOPE_COLORS[min(depth, len(SCOPE_COLORS) - 1)])
            for name, data in scope.items():
                row = self.rowCount()
                self.insertRow(row)
                for col, text in enumerate([
                    name,
                    str(data['value']),
                    data['data_type'],
                    label,
                ]):
                    item = QTableWidgetItem(text)
                    item.setBackground(bg)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.setItem(row, col, item)

    def clear_display(self) -> None:
        self.setRowCount(0)