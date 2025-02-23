from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def __init__(self, original_stdout):
        super().__init__()
        self.original_stdout = original_stdout

    def write(self, text):
        self.text_written.emit(str(text))
        self.original_stdout.write(text)

    def flush(self):
        pass

    def fileno(self):
        # Return the file descriptor of sys.stdout to mimic its behavior
        return self.original_stdout.fileno()