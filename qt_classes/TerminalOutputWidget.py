import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtGui import QTextCharFormat, QColor
from qt_classes.EmittingStream import EmittingStream


BODY_FONT = QtGui.QFont('Consolas', 15)


class TerminalOutputWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.text_area = QTextEdit()
        self.text_area.setFont(BODY_FONT)
        self.text_area.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        self.setLayout(layout)

        # Redirect stdout to the custom stream
        self.stream = EmittingStream(sys.stdout)
        self.stream.text_written.connect(self.update_text_area)
        sys.stdout = self.stream

    def update_text_area(self, text):
        if "\033[32m" in text:  # ANSI code for green text
            # Remove the ANSI escape code
            clean_text = text.replace("\033[32m", "").replace("\033[0m", "")

            # Create a QTextCharFormat for green text
            green_format = QTextCharFormat()
            green_format.setForeground(QColor("green"))

            # Apply the green format to the text
            self.text_area.setCurrentCharFormat(green_format)
            self.text_area.insertPlainText(clean_text)

            # Reset the format to default
            default_format = QTextCharFormat()
            self.text_area.setCurrentCharFormat(default_format)
        elif "\033[31m" in text:  # ANSI code for red text
            # Remove the ANSI escape code
            clean_text = text.replace("\033[31m", "").replace("\033[0m", "")

            # Create a QTextCharFormat for red text
            red_format = QTextCharFormat()
            red_format.setForeground(QColor("red"))

            # Apply the red format to the text
            self.text_area.setCurrentCharFormat(red_format)
            self.text_area.insertPlainText(clean_text)

            # Reset the format to default
            default_format = QTextCharFormat()
            self.text_area.setCurrentCharFormat(default_format)
        else:
            # Insert plain text if no ANSI codes are found
            self.text_area.insertPlainText(text)
        self.text_area.ensureCursorVisible()
