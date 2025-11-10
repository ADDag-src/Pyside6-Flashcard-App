from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QSizePolicy,
                               QPushButton, QMessageBox, QHBoxLayout, QFontComboBox)


class StudyWindow(QWidget):
    def __init__(self, deck_name, deck_id, database_manager, mode):
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.mode = mode
        if self.mode == "learn":
            self.setWindowTitle(f"Learning new cards in deck: {self.deck_name}")
        else:
            self.setWindowTitle(f"Reviewing cards in deck: {self.deck_name}")
        self.setMinimumSize(805, 550)

        self.layout = QVBoxLayout()
