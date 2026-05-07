from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import QRegularExpression


class Highlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._rules = []

        def add_rule(pattern: str, color: str, bold: bool = False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            self._rules.append((QRegularExpression(pattern), fmt))

        # Keywords
        keywords = r'\b(if|else|while|function|return|print)\b'
        add_rule(keywords, '#C586C0', bold=True)

        # Boolean literals
        add_rule(r'\b(true|false)\b', '#569CD6', bold=True)

        # Float (must come before integer)
        add_rule(r'\b\d+\.\d+\b', '#B5CEA8')

        # Integer
        add_rule(r'\b\d+\b', '#B5CEA8')

        # String literals (single-quoted)
        add_rule(r"'[^']*'", '#CE9178')

        # Float operators
        add_rule(r'(\+\.|-\.|\*\.|/\.|==\.|!=\.|--.)', '#DCDCAA')

        # Integer operators
        add_rule(r'(\+|-|\*|/|==|!=|--|(?<!\+)\+(?!\+))', '#DCDCAA')

        # String concat
        add_rule(r'\+\+', '#DCDCAA')

        # Assignment
        add_rule(r'(?<!=)=(?!=)', '#D4D4D4')

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)