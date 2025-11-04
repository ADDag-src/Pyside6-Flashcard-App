from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QSizePolicy,
                               QPushButton, QMessageBox, QHBoxLayout, QFontComboBox)


class EditDeckWindow(QWidget):
    def __init__(self, deck_name, deck_id, database_manager):
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.database_manager = database_manager
        self.setWindowTitle("Edit a deck")
        self.setMinimumSize(805, 550)
